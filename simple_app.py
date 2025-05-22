from urllib.parse import parse_qs

def format_params(environ):
    method = environ.get("REQUEST_METHOD", "GET")
    query_string = environ.get("QUERY_STRING", "")
    get_data = parse_qs(query_string)

    post_data = {}
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            content_length = 0
        post_body = environ["wsgi.input"].read(content_length).decode("utf-8")
        post_data = parse_qs(post_body)

    response = "GET parameters:\n"
    response += f"{get_data}\n\n"
    response += "POST parameters:\n"
    response += f"{post_data}\n"
    return response.encode("utf-8")


def simple_app(environ, start_response):
    status = '200 OK'
    response_body = format_params(environ)
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]