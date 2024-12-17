
# Property Management System

## Overview
This project is a Property Management System developed using Django. It provides functionalities to manage properties, locations, and users, leveraging PostgreSQL with the PostGIS extension for geospatial data support.

The system includes:

- An intuitive **Django Admin Interface** for efficient management of properties and locations.
- A user-friendly interface for **property owners** to add, manage, and update their properties.

---

## Features

### 1. **Database Setup**
- **PostgreSQL**: Used as the primary database.
- **PostGIS Extension**: Enabled for handling geospatial data like property locations.

### 2. **Core Functionalities**
- **Location Management**: 
  - Hierarchical location nesting (Country -> State -> City) with geospatial support.
  - CSV import support for location data.
  
- **Accommodation Management**:
  - Property creation, update, and delete operations.
  - Automatic user association for added properties.
  - JSON fields for amenities and images.
  - Geolocation support via PostGIS.
  
- **Localized Descriptions**:
  - Support for multiple languages via the `LocalizeAccommodation` model.

### 3. **User and Role Management**
- **Property Owners**:
  - Can sign up and manage their properties.
  - Limited to adding, updating, and deleting their own properties.

- **Admin Users**:
  - If granted **Staff Status: Active**, admins can:
    - Add, update, and delete properties.
    - Access all properties in the Django Admin interface.
    - Manage locations and user roles.
  ***Note*** : Only the superuser has access to the Accommodation list containing all properties created by admin users. If you need to perform operations on the list of accommodations, you must log in as the superuser. Other admin users will not be able to view the full list of accommodations in the Django Admin interface.

### 4. **Geospatial Integration**
- Geolocation fields for precise mapping.
- **PostGIS-based PointField** for location coordinates.

### 5. **Admin Enhancements**
- Custom Admin Views for `Location`, `Accommodation`, and `LocalizeAccommodation`.
- Import/Export capabilities for `Location` via CSV.
- Filtering and search capabilities for better data management.

### 6. **Custom User Sign-Up**
- Property Owners can sign up via a dedicated page.
- The sign-up form includes validations for:
  - **Email**: Uniqueness check.
  - **Password**: Minimum 8 characters, with confirmation.
  - **Phone number**: Numeric validation.
- Admins review and approve sign-up requests.

### 7. **Frontend**
- Simplified property list views for logged-in users.
- Admin-only visibility for operations like creating or editing locations.

---

## Models

### 1. **Location**
- **ID**: Unique identifier (primary key).
- **Title**: Name of the location (Country, State, City).
- **Center**: Geolocation as a PostGIS Point.
- **Parent**: Foreign key to a parent location (e.g., State under Country).
- **Location Type**: Type of location (e.g., Country, State, City).
- **Country Code**: ISO country code.
- **State Abbreviation**, **City**, **Created/Updated timestamps**.

### 2. **Accommodation**
- **ID**: Unique identifier (primary key).
- **Title**, **Feed**, **Bedroom Count**, **Review Score**.
- **USD Rate**: Price in USD.
- **Center**: Geolocation as a PostGIS PointField.
- **Images**: Array of image URLs.
- **Amenities**: JSON field for additional features.
- **Location**: Foreign key to Location.
- **User**: Associated property owner.
- **Published Status**, **Created/Updated timestamps**.

### 3. **LocalizeAccommodation**
- **Property**: Foreign key to Accommodation.
- **Language**: Language code (e.g., "en", "es").
- **Description**: Localized description.
- **Policy**: JSON field for policies (e.g., pet policies).

---

## Setup Instructions (with Docker)

### 1. **Install Docker and Docker Compose**
Ensure that Docker and Docker Compose are installed on your machine. You can follow the official Docker installation guides:

- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### 2. **Build and Run the Project with Docker**
Clone the repository:
```bash
git clone https://github.com/fahiiiiii/InventoryManagement
cd InventoryManagement
```

Build and Start the Containers: This command will build the Docker images and start the containers for the web server and PostgreSQL database.
```bash
docker-compose up --build
```
The `--build` flag ensures that Docker rebuilds the images (useful if any changes are made to the Dockerfile or requirements).

Apply Migrations: After the containers are up and running, you need to apply the database migrations to set up your database schema.
```bash
docker exec -it django_web python manage.py migrate
```

Create a Superuser (Admin User): Create a superuser to access the Django Admin interface.
```bash
docker exec -it django_web python manage.py createsuperuser
```
Follow the prompts to create the superuser account.

Access the Django Development Server: Visit http://127.0.0.1:8000 in your browser to see the Django application running.

Visit http://127.0.0.1:8000/admin to access the Django Admin Interface using the superuser credentials you just created.

### 3. **Docker Compose Services Overview**
- **db**: PostgreSQL with PostGIS extension for handling geospatial data.
- **web**: Django web service running the application, available at port 8000.
- **pgadmin**: PGAdmin service to manage your PostgreSQL database, available at port 5050 on your local machine.

### 4. **Stopping and Restarting the Containers**
To stop the containers:
```bash
docker-compose down
```
To restart the containers:
```bash
docker-compose up
```

## Populate Locations using Fixtures

If you have a CSV or JSON file containing location data, you can use Django's `loaddata` command to populate the database.

### Steps to Load Location Data

1. **Create a Location Fixture**:

   Ensure you have a `locations.json` file in the `fixtures/` directory or in any directory of your project. Here's an example of a `locations.json` file:

   ```json
   [
       {
           "model": "inventory.location",
           "pk": "1",
           "fields": {
               "title": "New York",
               "country_code": "US",
               "location_type": "City",
               "parent": null,
               "center": "POINT(-74.006 40.7128)"
           }
       },
       {
           "model": "inventory.location",
           "pk": "2",
           "fields": {
               "title": "California",
               "country_code": "US",
               "location_type": "State",
               "parent": null,
               "center": "POINT(-119.4179 36.7783)"
           }
       }
   ]
2. **Run the Command to Load the Data**:

    After the locations.json file is ready, you can load the data into your database by running the following command in the terminal:

    
    ```bash
    docker exec -it django_web python manage.py loaddata fixtures/locations.json
    ```
    This command will import the data into the Location model. The Location model should have fields such as title, country_code, location_type, parent, and center.

    


### 5. **Access the Django Admin Interface**
Visit http://127.0.0.1:8000/admin to manage properties and locations.

### 6. **Docker-Related Commands for Running and Managing the Application**
Run Django Commands Inside the Container (e.g., migrate, createsuperuser):
```bash
docker exec -it django_web python manage.py runserver
```
Run a custom Django command (for example, to generate sitemap):
```bash
docker exec -it django_web python manage.py generate_sitemap
```

Viewing Logs (for debugging):
```bash
docker-compose logs
```

---

## Usage

### 1. **Property Owner Signup**
Visit the Property Owner Signup page at:
```bash
/property-owner-signup/
```
Fill in the form with your details:
- Username
- Email
- Password (and confirmation)
- Phone number
- Location

After successful signup:
- Your request will be reviewed by the admin.
- Once approved, you can log in to manage your properties.

### 2. **Login**
Visit the Login page at:
```bash
/login/
```
Enter your credentials to access your account.

### 3. **Creating, Updating, and Deleting Properties**
For **Admin Users**:
- If a user is assigned **Staff Status: Active**, they can:
  - Create properties via the Add Property page.
  - Update properties via the Update Property option in the property list.
  - Delete properties from the property list.
  - Admins can view and manage all properties in the Django Admin interface.

For **Property Owners**:
- Logged-in property owners can:
  - Add properties via the Add Property page.
  - Edit or delete their own properties.
  - Property Owners cannot manage properties added by other users.
"***Important***: Only the superuser can view and manage all properties created by admin users. Admins without superuser privileges will not be able to access the full list of accommodations.Accomodation is disabled for all other users except the superuser."

---

## Custom Commands

### **Generate Sitemap**
Generate a sitemap.json for all country locations:
```bash
python manage.py generate_sitemap
```

---

## Testing
To run the tests and ensure code functionality and stability, follow these steps:

1. **Run Tests with Coverage**:
   ```bash
   docker exec -it django_web coverage run --source='inventory' manage.py test
   ```

2. **Generate Coverage Report**:
   ```bash
   docker exec -it django_web coverage report -m
   ```

This will run all tests and generate a coverage report.

---

## Contribution
- Fork the repository.
- Create a feature branch.
- Submit a pull request.

---

## License
This project is licensed under the MIT License.
