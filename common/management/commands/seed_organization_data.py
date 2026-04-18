from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from departments.models import Department, Division
from designations.models import Designation, Grade


DEPARTMENT_DIVISIONS = {
    "Steel": [
        "US Tekla - Thane",
        "US Tekla - Navi Mumbai",
        "Tekla Chennai",
        "SDS2",
    ],
    "Concrete": [
        "Precast Non US",
        "Rebar US",
        "Rebar Non US",
        "RDT-II",
    ],
    "BIM": [
        "BIM Infra",
        "BIM Arc",
        "BIM MEP",
    ],
    "Plant": [
        "Plant Engineering",
    ],
    "Software Development Services": [
        "SDS",
    ],
}

DESIGNATIONS = [
    "MD",
    "HOD",
    "Manager",
    "TL",
    "Checker",
    "Detailer",
    "Modeller",
]

GRADES = [
    "Jr",
    "Sr",
]


class Command(BaseCommand):
    help = "Seed departments, divisions, grades, and designations"

    def handle(self, *args, **kwargs):
        created_by = self._get_default_admin()

        self.stdout.write(self.style.NOTICE("Seeding organization master data..."))

        department_count = 0
        division_count = 0
        for department_name, division_names in DEPARTMENT_DIVISIONS.items():
            department, _ = self._get_or_create_department(department_name, created_by)
            department_count += 1

            for division_name in division_names:
                self._get_or_create_division(department, division_name, created_by)
                division_count += 1

        grade_count = 0
        for grade_name in GRADES:
            self._get_or_create_grade(grade_name)
            grade_count += 1

        designation_count = 0
        for designation_name in DESIGNATIONS:
            self._get_or_create_designation(designation_name, created_by)
            designation_count += 1

        self.stdout.write(self.style.SUCCESS(f"Departments seeded: {department_count}"))
        self.stdout.write(self.style.SUCCESS(f"Divisions seeded: {division_count}"))
        self.stdout.write(self.style.SUCCESS(f"Grades seeded: {grade_count}"))
        self.stdout.write(self.style.SUCCESS(f"Designations seeded: {designation_count}"))
        self.stdout.write(self.style.SUCCESS("Organization seeder completed successfully"))

    def _get_default_admin(self):
        User = get_user_model()
        return User.objects.filter(employee_code="0001").first()

    def _get_or_create_department(self, name, user):
        department = Department.objects.filter(name__iexact=name).first()
        if department:
            if department.name != name or not department.is_active:
                department.name = name
                department.is_active = True
                department.updated_by = user
                department.save(update_fields=["name", "is_active", "updated_by", "updated_at"])
            return department, False

        return Department.objects.create(
            name=name,
            is_active=True,
            created_by=user,
            updated_by=user,
        ), True

    def _get_or_create_division(self, department, name, user):
        division = Division.objects.filter(department=department, name__iexact=name).first()
        if division:
            if division.name != name or not division.is_active:
                division.name = name
                division.is_active = True
                division.updated_by = user
                division.save(update_fields=["name", "is_active", "updated_by", "updated_at"])
            return division, False

        return Division.objects.create(
            department=department,
            name=name,
            is_active=True,
            created_by=user,
            updated_by=user,
        ), True

    def _get_or_create_grade(self, name):
        grade = Grade.objects.filter(name__iexact=name).first()
        if grade:
            if grade.name != name or not grade.is_active:
                grade.name = name
                grade.is_active = True
                grade.save(update_fields=["name", "is_active"])
            return grade, False

        return Grade.objects.create(name=name, is_active=True), True

    def _get_or_create_designation(self, name, user):
        designation = Designation.objects.filter(name__iexact=name, grade__isnull=True).first()
        if designation:
            if designation.name != name or not designation.is_active:
                designation.name = name
                designation.is_active = True
                designation.updated_by = user
                designation.save(update_fields=["name", "is_active", "updated_by", "updated_at"])
            return designation, False

        return Designation.objects.create(
            name=name,
            grade=None,
            is_active=True,
            created_by=user,
            updated_by=user,
        ), True
