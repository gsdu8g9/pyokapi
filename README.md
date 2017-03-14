# pyokapi
Python Wrapper for the Odnoklassniki API

## Usage
    import pyokapi
    
    
    application = pyokapi.application(
        '',  # application id
        '',  # application key
        '',  # application secret key
        ''   # redirec uri
    )
    with AutoCleintOauthSession(
        application,
        ['VALUABLE_ACCESS', 'LONG_ACCESS_TOKEN'],
        '',  # ok.ru username
        '',  # ok.ru password
        session_data_filename='session.dat'
    ) as session:
        api = pyokapi.API(session)
        print(api.users.hasAppPermission(ext_perm='SET_STATUS'))
