from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Room, RoomImage, Guest, Booking, TeamMember,FoodItem, CustomUser

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3  # Number of empty image upload slots

class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomImageInline]
    list_display = ['room_number', 'room_type', 'get_image_count']
    
    def get_image_count(self, obj):
        return obj.images.count()
    get_image_count.short_description = 'Image Count'

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'proof_type')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('proof_type',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('guest', 'room', 'check_in', 'check_out', 'total_amount', 'payment_type')
    list_filter = ('payment_type', 'room__room_type')
    search_fields = ('guest__name', 'room__room_number')
    date_hierarchy = 'check_in'

admin.site.register(TeamMember)

admin.site.register(FoodItem)

admin.site.register(Room, RoomAdmin)
admin.site.register(RoomImage)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    
    # Update fieldsets to include user_type in the right section
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Update add_fieldsets to include user_type when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
