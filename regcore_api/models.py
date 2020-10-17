import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey


class Discount(models.Model):
    code_name = models.CharField(max_length=100)
    percent_off = models.IntegerField(null=True)
    amount_off = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    single_use = models.BooleanField(default=False)
    used = models.IntegerField(default=0)
    reason = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.code_name

    def isValid(self):
        now = timezone.now()
        if self.start_date > now or self.end_date < now:
            return False
        if self.single_use and self.used > 0:
            return False
        return True


class Charity(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(
        max_length=500, verbose_name="URL", help_text="Charity link", blank=True
    )
    donations = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="External donations to add to metrics",
    )

    class Meta:
        verbose_name_plural = "Charities"


class Event(models.Model):
    dealer_reg_star = models.DateTimeField(
        verbose_name="Dealer Registration Start",
        help_text="Start date and time for dealer applications",
    )
    dealer_reg_end = models.DateTimeField(verbose_name="Dealer Registration End")
    staff_reg_start = models.DateTimeField(
        verbose_name="Staff Registration Start", help_text="(Not currently enforced)"
    )
    staff_reg_end = models.DateTimeField(verbose_name="Staff Registration End")
    attendee_reg_start = models.DateTimeField(
        verbose_name="Attendee Registration Start"
    )
    attendee_reg_end = models.DateTimeField(verbose_name="Attendee Registration End")
    onsite_reg_start = models.DateTimeField(
        "On-site Registration Start",
        help_text="Start time for /registration/onsite form",
    )
    onsite_reg_end = models.DateTimeField(verbose_name="On-site Registration End")
    event_start = models.DateField(verbose_name="Event Start Date")
    event_end = models.DateField(verbose_name="Event End Date")
    registration_email = models.CharField(
        max_length=200,
        verbose_name="Registration Email",
        help_text="Email to display on error messages for attendee registration",
        blank=True,
    )
    staff_email = models.CharField(
        max_length=200,
        verbose_name="Staff Email",
        help_text="Email to display on error messages for staff registration",
        blank=True,
    )
    dealer_email = models.CharField(
        max_length=200,
        verbose_name="Dealer Email",
        help_text="Email to display on error messages for dealer registration",
        blank=True,
    )
    code_of_conduct = models.FileField(
        upload_to="codes_of_conduct/%Y/%m/%d", blank=True, null=True
    )
    charity = models.ForeignKey(
        Charity, null=True, blank=True, on_delete=models.SET_NULL
    )


class Merchandise(models.Model):
    SHIRT = "S"
    ACCESSORY = "A"
    BOOK = "B"
    MISC = "MISC"
    CATEGORY_CHOICES = [
        (SHIRT, "Shirt"),
        (ACCESSORY, "Accessory"),
        (BOOK, "Book"),
        (MISC, "Misc."),
    ]
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES,)


class PriceLevelOption(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    merch = models.ForeignKey(Merchandise, on_delete=models.CASCADE)
    option_image = models.ImageField(
        upload_to="price_level/%Y/%m/%d", blank=True, null=True
    )
    active = models.BooleanField(default=False)
    rank = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    public = models.BooleanField()

    def __str__(self):
        return "{0} (${1})".format(self.name, self.price)


class Department(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class EmergencyContact(models.Model):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    relation = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=15, default="XXXXXXXXXX")
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Person(models.Model):
    class Meta:
        abstract = True

    SHIRT_SIZE_CHOICES = [
        ("XS", "extra small"),
        ("SM", "small"),
        ("MD", "medium"),
        ("L", "large"),
        ("XL", "extra large"),
        ("XXL", "extra extra large"),
    ]

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    badge_name = models.CharField(max_length=32)
    email = models.EmailField()
    pronouns = models.CharField(max_length=32)
    emergency_contacts = GenericRelation(EmergencyContact)
    # special_medical = models.TextField(blank=True)
    shirt_size = models.CharField(max_length=3, choices=SHIRT_SIZE_CHOICES)
    birth_date = models.DateField()
    agrees_to_con_tos = models.BooleanField()
    delete_info = models.BooleanField(blank=True)
    # Banned
    is_banned = models.BooleanField(blank=True)
    reason = models.TextField(blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Attendee(Person):
    # billing
    address1 = models.CharField("Address line 1", max_length=1024,)
    address2 = models.CharField("Address line 2", max_length=1024,)
    zip_code = models.CharField("ZIP / Postal code", max_length=12,)
    city = models.CharField("City", max_length=1024,)
    state = models.CharField("State", max_length=64)
    country = CountryField()
    phone_number = models.CharField(max_length=15, default="XXXXXXXXXX")
    # emails/surveys
    agrees_to_surveys = models.BooleanField()
    request_volunteer_info = models.BooleanField()
    request_asl = models.BooleanField()

    def __str__(self):
        return self.full_name


class Staff(Person):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    supervisor = models.ForeignKey("self", on_delete=models.CASCADE)
    needs_room = models.BooleanField()
    special_skills = models.TextField(blank=True)
    checked_in = models.BooleanField()
    diet_restrictions = models.TextField(blank=True)
    department_head = models.BooleanField()

    def __str__(self):
        return self.full_name

