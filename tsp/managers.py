from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """Create student union, society and student users."""

    def create_user(self, email, password, **other_fields):
        """
        Create and save a user with the given email and password.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str
            The password for the user.
        other_fields : dict
            Additional fields to save for the user.

        Returns
        -------
        User
            The created user object.
        """
        
        if not email:
            raise ValueError(
                'Email address is required.'
            )
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **other_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_student_union(self, email, password, name, **other_fields):
        """
        Create and save a student union user with the given email, password, 
        and name.

        Parameters
        ----------
        email : str
            The email address of the student union user.
        password : str
            The password for the student union user.
        name : str
            The name of the student union.
        other_fields : dict
            Additional fields to save for the student union user.

        Returns
        -------
        User
            The created student union user object.
        """
        
        other_fields.setdefault('is_superuser', True)
        return self.create_user(
            email, password, name, **other_fields
        )

    def create_society(self, email, password, name, **other_fields):
        """
        Create and save a society user with the given email, password, name, 
        and member discount.

        Parameters
        ----------
        email : str
            The email address of the society user.
        password : str
            The password for the society user.
        name : str
            The name of the society.
        member_discount : int
            The member discount for the society.
        other_fields : dict
            Additional fields to save for the society user.

        Returns
        -------
        User
            The created society user object.
        """

        return self.create_user(
            email, password, name, **other_fields
        )

    def create_student(self, email, password,
                       first_name, last_name, **other_fields):
        """
        Create and save a student user with the given email, password, 
        first name, and last name.

        Parameters
        ----------
        email : str
            The email address of the student user.
        password : str
            The password for the student user.
        first_name : str
            The first name of the student.
        last_name : str
            The last name of the student.
        other_fields : dict
            Additional fields to save for the student user.

        Returns
        -------
        User
            The created student user object.
        """
        
        return self.create_user(
            email, password, first_name, last_name, **other_fields
        )


class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        """
        Get a queryset of student objects filtered by role.
        
        Returns
        -------
        QuerySet
            A queryset of student objects.
        """

        results = super().get_queryset(*args, **kwargs)
        return results.filter(role='STUDENT')


class SocietyManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        """
        Get a queryset of society objects filtered by role.
        
        Returns
        -------
        QuerySet
            A queryset of society objects.
        """

        results = super().get_queryset(*args, **kwargs)
        return results.filter(role='SOCIETY')


class StudentUnionManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        """
        Get a queryset of student union objects filtered by role.
        
        Returns
        -------
        QuerySet
            A queryset of student union objects.
        """

        results = super().get_queryset(*args, **kwargs)
        return results.filter(role='STUDENT_UNION')
