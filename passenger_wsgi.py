import sys, os

INTERP = os.path.join(os.environ['HOME'], 'brew-journal.com', 'brewjournal', 'env', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(),'brewjournal'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'brewjournal.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

usePaste = False
debug = False
if usePaste:
    # sys.path += ['/home/jsled/brew-journal.com']
    from paste.exceptions.errormiddleware import ErrorMiddleware
    if debug:
        # To cut django out of the loop, comment the above application = ... line ,
        # and remove "test" from the below function definition.
        def testapplication(environ, start_response):
            status = '200 OK'
            output = 'Hello World! Running Python version ' + sys.version + '\n\n'
            response_headers = [('Content-type', 'text/plain'),
                                ('Content-Length', str(len(output)))]
            # to test paste's error catching prowess, uncomment the following line
            # while this function is the "application"
            # raise("error")
            start_response(status, response_headers)    
            return [output]
        application = ErrorMiddleware(testapplication, debug=True)
    else:
        application = ErrorMiddleware(application, debug=True)
