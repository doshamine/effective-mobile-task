from django.db import models

class User(models.Model):
    __tablename__ = 'users'

    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=255, blank=False, null=False)
    is_active = models.BooleanField(null=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField('Role', through='UserRoles', related_name='users')


class Role(models.Model):
    __tablename__ = 'roles'

    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    display_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    description = models.TextField()
    permissions = models.ManyToManyField('Permission', through='RolePermissions', related_name='roles')


class UserRoles(models.Model):
    __tablename__ = 'user_roles'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    valid_until = models.DateTimeField(null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='uq_user_roles_user_role'
            )
        ]


class Permission(models.Model):
    __tablename__ = 'permissions'

    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField()


class RolePermissions(models.Model):
    __tablename__ = 'role_permissions'

    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'],
                name='uq_role_permissions_role_permission'
            )
        ]
