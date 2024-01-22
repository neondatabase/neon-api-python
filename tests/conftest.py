def neon():
    from neon_client import NeonAPI

    return NeonAPI.from_environ()
