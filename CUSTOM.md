# leela customizations
Document here any customizations you do to leela for your organization.
Any customization in leela is configured in the custom settings file at `leela/settings/custom.py`.

The place to write custom code is always the `custom/` module.

## Requirements
Use the requirement file `requirements/custom.txt` to add all the requirements that your extensions and custom code is going to need.

## Template filters
Apart from the filters that jinja2 [offers](http://jinja.pocoo.org/docs/dev/templates/#filters), you can implement your own.

To add new template filters, define them in the file `custom/filters.py` following the jinja2 guidelines. Add tests for your filters in `custom/tests/test_filters.py`. Next, just activate them in the custom settings file using the `FILTERS` variable:

    FILTERS = (
        ('myfiltername', 'import.path.to.my.filter.function'),
    )

## Authentication
To manage the admin panel you need to authenticate.

You can build your own authentication method for the admin panel. Write your authentication backends in `custom/auth.py` following the [Django guidelines](https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#writing-an-authentication-backend) and configure them in the custom settings file like this:

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'custom.auth.LDAPBackend'
    )

## Spam checks
The system allow spam checks configuration through configuration. Build your check in `custom/spamchecks.py`. An spam check function have to return either `True` when the email is considered spam, or `False` when it is considered ham. For example:

    def has_href(entry):
        """Report as spam if 'href' appears in the text."""
        for key in entry.context:
            if 'href' in entry.context[key]:
                return True
        return False

If we want to configure this check for our `EmaiKind` with the name `my_lovely_email`, we would add this to the custom settings file:

    SPAM_CHECK = {
        'my_lovely_email': ('custom.spamchecks.has_href',)
    }

We can add multiple checks to this tuple, and the `EmailEntry` will be marked as spam and not sent if any of these checks report it as spam.

## API extensions and complex customizations
leela provides a basic API to retrieve information from the backend. You probably need to extend it, for example to expose a complex customization.

Add your customization module into `custom/`, like `custom/myextension/[views.py, urls.py, models.py,...]`. Then, add your module `custom.myextension` in the `INSTALLED_APPS` setting. Finally, subscribe your urls in `custom/urls.py` the Django way:

    api_urlpatterns = [
        url(r'^extension/(?P<customer_id>[0-9]+)/$',
            extension_view,
            name='extension')
    ]


Keep in mind that these urls will be automatically loaded for you, and prefixed by `/api/`. So in the example above, a valid url path matching the pattern would be: `/api/extension/2121212/`.

## Custom email backends
You can add email backends to send entries through SMTP servers, signed SMTP servers, Mandrill, etc.

To add a new backend, you need to create two classes:
- An EmailBackend subclass of [`BaseEmailBackend`](https://docs.djangoproject.com/en/dev/topics/email/#email-backends), capable of managing [`EmailMultiAlternatives`](https://docs.djangoproject.com/en/dev/topics/email/#sending-alternative-content-types).
- A `ResponseManager` subclass of `emails.backends.BaseResponseManager` that will manage the response of the `EmailBackend` added to the `EmailMultiAlternatives` instance. The method `process_response` should return `True` or `False` if the sending was successful depending on the data in the `EmailMultiAlternatives`. The method can also update the thirdparty_id of the entry if convenient (will be saved in DB for you). It must not raise an exception in any case.

To configure the new backend, use the setting `CUSTOM_EMAIL_BACKENDS`:

    CUSTOM_EMAIL_BACKENDS = (
        ('mynewbackend',
         'path.to.my.new.backend',
         'path.to.my.response.manager'
        ),
    )

Next entries to send through that backend have to include the param `"backend": "mynewbackend"` in the scheduling to be sent with it.
