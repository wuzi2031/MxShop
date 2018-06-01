from rest_framework import status


def send_verify_code(mobile,code):
    print(code)
    return status.HTTP_200_OK


if __name__ == '__main__':
    send_verify_code("")
