
-- Create staging schema 
CREATE SCHEMA IF NOT EXISTS staging;
-- Grant permissions to the staging schema
GRANT USAGE ON SCHEMA staging TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA staging TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA staging TO PUBLIC;       

CREATE TABLE IF NOT EXISTS staging.RENTAL_OFFICES
(   OfficeName VARCHAR(255) PRIMARY KEY,
    City VARCHAR(255),
    Area VARCHAR(255),
    State VARCHAR(255),
    Country VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS staging.CARS
(   Plate VARCHAR(255) PRIMARY KEY,
    Category VARCHAR(255),
    Model VARCHAR(255),
    Brand VARCHAR(255),
    Fuel VARCHAR(255),
    RegistrationDate DATE
);

--HAVE_OPTIONAL(Plate:CARS,Optional)
CREATE TABLE IF NOT EXISTS staging.HAVE_OPTIONAL
(   Plate VARCHAR(255) PRIMARY KEY,
    Optional VARCHAR(255),
    FOREIGN KEY (Plate) REFERENCES staging.CARS(Plate)
);


--RENTALS(Plate:CARS,PickupDate,DropoffDate,PickupPlace:RENTAL_OFFICES,DropoffPlace:RENTAL_OFFICES,Miles) 

CREATE TABLE IF NOT EXISTS staging.RENTALS
(
    Plate           VARCHAR(255),
    PickupDate      DATE,
    DropoffDate     DATE,
    PickupPlace     VARCHAR(255),
    DropoffPlace    VARCHAR(255),
    Miles           INT,

    PRIMARY KEY (Plate, PickupDate),

    FOREIGN KEY (Plate) 
        REFERENCES staging.CARS(Plate),
    FOREIGN KEY (PickupPlace) 
        REFERENCES staging.RENTAL_OFFICES(OfficeName),
    FOREIGN KEY (DropoffPlace) 
        REFERENCES staging.RENTAL_OFFICES(OfficeName)
);

--DRIVERS(LicenseNumber,LicenseExpiration,DriverName,Birthdate)
CREATE TABLE IF NOT EXISTS staging.DRIVERS
(
    LicenseNumber VARCHAR(255) PRIMARY KEY,
    LicenseExpiration DATE,
    DriverName VARCHAR(255),
    Birthdate DATE
);

--DRIVE(LicenseNumber:DRIVERS,(Plate,PickupDate):RENTALS)

CREATE TABLE IF NOT EXISTS staging.DRIVE
(
    LicenseNumber VARCHAR (255), 
    Plate VARCHAR(255),
    PickupDate DATE,

    PRIMARY KEY (LicenseNumber, Plate, PickupDate),
    FOREIGN KEY (LicenseNumber) 
        REFERENCES staging.DRIVERS(LicenseNumber),  
    FOREIGN KEY (Plate, PickupDate)
        REFERENCES staging.RENTALS(Plate, PickupDate)
);


--INSURANCES(Risk,(Plate,PickupDate):RENTALS,Cost)

 CREATE TABLE IF NOT EXISTS staging.INSURANCES
( 
    Risk VARCHAR(255),
    Plate VARCHAR(255),
    PickupDate DATE,
    Cost DECIMAL(10, 2),    
    PRIMARY KEY (Risk, Plate, PickupDate),
    FOREIGN KEY ( Plate, PickupDate)
        REFERENCES staging.RENTALS(Plate, PickupDate)
);

--PAYMENTS((Plate,PickupDate):RENTALS,Amount,Discount,PaymentMode) 

CREATE TABLE IF NOT EXISTS staging.PAYMENTS
(
    Plate VARCHAR(255),
    PickupDate DATE,
    Amount DECIMAL(10, 2),
    Discount DECIMAL(10, 2),
    PaymentMode VARCHAR(255),

    PRIMARY KEY (Plate, PickupDate),
    FOREIGN KEY (Plate, PickupDate)
        REFERENCES staging.RENTALS(Plate, PickupDate)
);







