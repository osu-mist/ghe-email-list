import requests
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='List emails for users in github enterprise'
            )
    parser.add_argument(
            '--token', '-t',
            dest='token',
            help='Access token with user:email scope',
            required=True
            )
    arguments = parser.parse_args()
    token = arguments.token
    users_endpoint = "https://github.sig.oregonstate.edu/api/v3/users"

    # This list may include suspended users
    usernames = []
    users_url = users_endpoint + "?since=0"

    while True:
        users_response = requests.get(
               users_url,
               auth=(None, token)
               )

        users_data = users_response.json()

        if len(users_data) == 0:
            break
        else:
            users_url = users_response.links['next']['url']

            usernames.extend(
                    [user['login'] for user in users_data
                        if user['type'] == "User" and user['login'] != "ghost"]
                    )

    unsuspended_emails = []

    for user in usernames:
        print("-----Processing: %s-----" % user)
        user_response = requests.get(
                "%s/%s" % (users_endpoint, user),
                auth=(None, token)
                )

        user_data = user_response.json()

        if not user_data['suspended_at']:
            print("Not suspended")
            if user_data['email']:
                print("Has public email")
                unsuspended_emails.append(user_data['email'])
            else:
                default_email = "%s@oregonstate.edu" % user
                print("No public email, defaulting to %s" % default_email)
                unsuspended_emails.append(default_email)
        else:
            print("Suspended")

    print(*unsuspended_emails, sep=', ')
