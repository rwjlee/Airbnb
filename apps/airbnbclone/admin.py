from django.contrib import admin

# Register your models here.

import apps.airbnbclone.models as m

admin.site.register(m.Amenity)
admin.site.register(m.User)
admin.site.register(m.Conversation)
admin.site.register(m.Message)
admin.site.register(m.Listing)