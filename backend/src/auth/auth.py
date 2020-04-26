import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


# these are our domain in the authorization system
AUTH0_DOMAIN = 'freenano.auth0.com'
# This is a hashing algorithm.
ALGORITHMS = ['RS256']
# this is a unique identifier of our API in the authorization system
API_AUDIENCE = 'coffee_id'

# https://freenano.auth0.com/authorize?audience=coffee_id&response_type=token&client_id=X8Z5tbB5VDXgIzn6JQVbyde9lIgHbCQI&redirect_uri=http://localhost:8080/login-results

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


'''

@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


# Get the function and initial processing of the token.
def get_token_auth_header():

    # We get the whole result returned from the authentication system.
    auth = request.headers.get('Authorization', None)
    # Check if there is a result?, if not,
    # immediately return the error code is not authorized
    if not auth:
        raise AuthError(
            {
                'code': 'authorization_header_missing',
                'description': 'error, authorization is still pending.'
            }, 401)

    # separate and place the keyword and token  in one array
    result = auth.split()

    # checking the keyword 'bearer', raise error if not
    if result[0].lower() != 'bearer':
        raise AuthError(
            {
                'code':
                'invalid_header',
                'description':
                'error, authorization header must start with "Bearer".'
            }, 401)

    # auth header must have 2 parts
    elif len(result) != 2:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Token not found.'
            }, 401)

    # If everything goes well, the token and return it
    token = result[1]
    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission
    string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    # checks for user permissions obtained from the token
    if 'permissions' not in payload:
        raise AuthError(
            {
                'code': 'invalid_claims',
                'description': 'Error. Sorry, you do not have any permission.'
            }, 400)

    # ensure that user permissions from the payload
    # contain permissions for this route
    if permission not in payload['permissions']:
        raise AuthError(
            {
                'code': 'unauthorized',
                'description':
                'Sorry, you do not have permission on this page.'
            }, 401)

    # If everything is OK, return True.
    return True


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)
    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload
    !!NOTE urlopen has a common certificate error described

'''


def verify_decode_jwt(token):
    # get public key from authorization system
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # get header data from token
    unverified_header = jwt.get_unverified_header(token)

    # choose rsa key
    rsa_key = {}

    # validate token header contains kid
    if 'kid' not in unverified_header:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

    for key in jwks['keys']:
        # if kid match, build rsa key
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # validate the token
            payload = jwt.decode(token,
                                 rsa_key,
                                 algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')

            return payload

        # catch common errors

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 401)

        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    'code':
                    'invalid_claims',
                    'description':
                    'Incorrect claims. Please, check the audience and issuer.'
                }, 401)
        except Exception:
            raise AuthError(
                {
                    'code': 'invalid_header',
                    'description': 'Unable to parse authentication token.'
                }, 400)
    raise AuthError(
        {
            'code': 'invalid_header',
            'description': 'Unable to find the appropriate key.'
        }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
