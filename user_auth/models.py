from django.db import models

from effective_mobile_task import settings


class Role(models.Model):
    __tablename__ = "roles"

    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    display_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    description = models.TextField()
    permissions = models.ManyToManyField(
        "Permission", through="RolePermissions", related_name="roles"
    )

    def __str__(self):
        return self.display_name


def get_default_role_pk() -> int:
    role = Role.objects.get(name=settings.DEFAULT_ROLE)
    return role.pk


class Permission(models.Model):
    __tablename__ = "permissions"

    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    description = models.TextField()


class RolePermissions(models.Model):
    __tablename__ = "role_permissions"

    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["role", "permission"]


class User(models.Model):
    __tablename__ = "users"

    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(
        "Role",
        related_name="users",
        on_delete=models.PROTECT,
        default=get_default_role_pk,
    )


class RefreshToken(models.Model):
    __tablename__ = "refresh_tokens"

    jti = models.CharField(
        max_length=36, primary_key=True, unique=True, blank=False, null=False
    )
    subject = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="refresh_tokens"
    )
