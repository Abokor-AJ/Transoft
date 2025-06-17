from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, FreightCompany, EndCustomer
from django.db import transaction
import random
from superadmin.models import SaaSProvider

class Command(BaseCommand):
    help = 'Seeds the database with a hierarchy of SaaS provider, freight companies, and end customers'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed the database...')
        
        with transaction.atomic():
            # Create SaaS Provider
            self.stdout.write('Creating SaaS Provider...')
            saas_provider = self.create_saas_provider()
            
            # Create Freight Companies
            self.stdout.write('Creating Freight Companies...')
            freight_companies = self.create_freight_companies(saas_provider)
            
            # Create End Customers
            self.stdout.write('Creating End Customers...')
            end_customers = self.create_end_customers(freight_companies)
            
            # Verify Data Isolation
            self.stdout.write('Verifying Data Isolation...')
            self.verify_data_isolation(saas_provider, freight_companies, end_customers)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))

    def create_saas_provider(self):
        # Create SaaS Provider
        saas = SaaSProvider.objects.create(
            name='Main SaaS Provider',
            contact_email='saas@example.com'
        )
        # Create SaaS Provider User
        saas_user = User.objects.create_user(
            username='saas_admin',
            email='saas@example.com',
            password='saas123'
        )
        # Create SaaS Provider Profile
        saas_profile = UserProfile.objects.create(
            user=saas_user,
            user_type=UserProfile.UserType.SAAS_PROVIDER
        )
        return saas

    def create_freight_companies(self, saas_provider):
        companies = []
        for i in range(3):
            # Create Freight Company
            company = FreightCompany.objects.create(
                name=f'Freight Company {i+1}',
                email=f'company{i+1}@example.com',
                phone=f'+1234567890{i}',
                address=f'Address {i+1}, City, Country',
                saas_provider=saas_provider
            )
            
            # Create Freight Company Admin
            admin_user = User.objects.create_user(
                username=f'freight_admin_{i+1}',
                email=f'admin{i+1}@company{i+1}.com',
                password='freight123'
            )
            
            # Create Freight Company Admin Profile
            admin_profile = UserProfile.objects.create(
                user=admin_user,
                user_type=UserProfile.UserType.FREIGHT_ADMIN,
                linked_company=company
            )
            
            companies.append(company)
        
        return companies

    def create_end_customers(self, freight_companies):
        customers = []
        for i in range(5):
            # Create End Customer
            customer = EndCustomer.objects.create(
                name=f'End Customer {i+1}',
                email=f'customer{i+1}@example.com',
                phone=f'+9876543210{i}',
                address=f'Customer Address {i+1}, City, Country'
            )
            
            # Link to 2-3 random freight companies
            num_companies = random.randint(2, 3)
            selected_companies = random.sample(freight_companies, num_companies)
            customer.freight_companies.set(selected_companies)
            
            # Create End Customer Admin
            admin_user = User.objects.create_user(
                username=f'customer_admin_{i+1}',
                email=f'admin{i+1}@customer{i+1}.com',
                password='customer123'
            )
            
            # Create End Customer Admin Profile
            admin_profile = UserProfile.objects.create(
                user=admin_user,
                user_type=UserProfile.UserType.END_CUSTOMER_ADMIN,
                linked_customer=customer
            )
            
            # Create 2-3 Staff Members
            for j in range(random.randint(2, 3)):
                staff_user = User.objects.create_user(
                    username=f'customer{i+1}_staff_{j+1}',
                    email=f'staff{j+1}@customer{i+1}.com',
                    password='staff123'
                )
                
                # Create Staff Profile
                staff_profile = UserProfile.objects.create(
                    user=staff_user,
                    user_type=UserProfile.UserType.END_CUSTOMER_STAFF,
                    linked_customer=customer
                )
            
            customers.append(customer)
        
        return customers

    def verify_data_isolation(self, saas_provider, freight_companies, end_customers):
        # Verify SaaS Provider Access
        self.stdout.write('Verifying SaaS Provider Access...')
        saas_companies = FreightCompany.objects.all()
        self.stdout.write(f'SaaS Provider can see {saas_companies.count()} freight companies')
        
        # Verify Freight Company Admin Access
        self.stdout.write('Verifying Freight Company Admin Access...')
        for company in freight_companies:
            admin = UserProfile.objects.get(linked_company=company)
            customers = EndCustomer.objects.filter(freight_companies=company)
            self.stdout.write(f'Freight Company {company.name} admin can see {customers.count()} customers')
        
        # Verify End Customer Admin Access
        self.stdout.write('Verifying End Customer Admin Access...')
        for customer in end_customers:
            admin = UserProfile.objects.get(linked_customer=customer, user_type=UserProfile.UserType.END_CUSTOMER_ADMIN)
            providers = customer.freight_companies.all()
            self.stdout.write(f'End Customer {customer.name} admin can see {providers.count()} freight companies')
            
            # Verify Staff Access
            staff = UserProfile.objects.filter(
                linked_customer=customer,
                user_type=UserProfile.UserType.END_CUSTOMER_STAFF
            )
            self.stdout.write(f'End Customer {customer.name} has {staff.count()} staff members') 