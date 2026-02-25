Create Database Hotel_Reservation_System;

Create Table Guests(
GuestID int auto_increment primary key,
FirstName varchar(100) not null,
LastName varchar(100) not null,
Email varchar(150) not null UNIQUE,
Phone varchar(20) null,
NationalID varchar(20) not null UNIQUE
);

Create Table RoomTypes(
RoomTypeID int auto_increment primary key,
TypeName varchar(100) not null,
Description text,
Capacity int not null,
PricePerNight decimal(10,2) not null
);

Create Table Rooms(
RoomID int auto_increment primary key,
RoomTypeID int not null,
RoomNumber varchar(10) not null UNIQUE,
Floor int null,
Room_Status varchar(50) not null,
foreign key(RoomTypeID) references RoomTypes(RoomTypeID)
);

Create Table Reservations(
ReservationID int auto_increment primary key,
GuestID INT not null,
RoomID INT not null,
BookingDate date not null,
CheckInDate date not null,
CheckOutDate date not null,
TotalAmount DECIMAL(10,2) not null,
ReservationStatus varchar(50) not null,
foreign key(GuestID) references Guests(GuestID),
foreign key(RoomID) references Rooms(RoomID),
CONSTRAINT CHK_DateOrder CHECK (CheckOutDate > CheckInDate),
CONSTRAINT CHK_BookingLogic CHECK (CheckInDate >= BookingDate),
CONSTRAINT CHK_TotalAmount CHECK (TotalAmount > 0)
);

Create Table Payments(
PaymentID int auto_increment primary key,
ReservationID int not null,
PaymentDate datetime not null,
Amount decimal(10,2) not null,
PaymentMethod varchar(50) not null,
PaymentStatus varchar(50) not null,
foreign key(ReservationID) references Reservations(ReservationID)
ON DELETE restrict
);

Insert into Guests(FirstName,LastName,Email,Phone,NationalID) values
('Kerem','YILMAZ','Kerem.Y@gmail.com','532-0101','11111111110'),
('Ayşe','YILDIRIM','Ayşe.Y@gmail.com','532-0102','22222222220'),
('Emre','ÖZKAN','Emre.Ö@gmail.com','532-0103','33333333330'),
('Michael','BROWN','Michael.B@gmail.com','532-0104','44444444440'),
('Hamit','Şahin','Hamit.Ş@gmail.com','532-0105','55555555550'),
('Zeynep','Öztürk','Zeynep.Ö@gmail.com','532-0106','66666666660'),
('Mustafa','ARSLAN','Mustafa.A@gmail.com','532-0107','77777777770'),
('John','SMITH','John.S@gmail.com','532-0108','88888888880'),
('Hüseyin','YILDIZ','Hüseyin.Y@gmail.com','532-0109','99999999990'),
('William','JONES','William.J@gmail.com','532-0110','10101010100');

Insert into RoomTypes(TypeName,Description,Capacity,PricePerNight) values
('Economy Single','Small,budget-friendly room without a view',1,80.00),
('Standard Single','Usual room for solo travelers',1,100.00),
('Standard Double','Comfortable room with two beds',2,200.00),
('Deluxe Suite','Luxury suite with city view and private terrace',2,500.00),
('Family Room','Spacious room for families with 4 beds',4,350.00),
('Presidential Suite','A presidential suite will consist of multiple rooms with opulent furnishings and amenities',30,1000.00),
('Bridal Suite','A suite of rooms in a hotel for the use of a newly married couple',2,500.00),
('Honeymoon Suite','A suite with special amenities primarily aimed at couples and newlyweds',2,650.00),
('King Suite','This is a type of hotel room that contains a larger double bed,namely the king size',8,800.00),
('Junior Suite','A spacious room with a small sitting area and king bed',2,280.00);

Insert into Rooms(RoomTypeID,RoomNumber,Floor,Room_Status) values
(1,'101',1,'Available'),
(2,'102',1,'Available'),
(3,'103',1,'Under Maintenance'),
(4,'201',2,'Available'),
(5,'202',2,'Available'),
(6,'203',2,'Occupied'),
(7,'301',3,'Available'),
(8,'302',3,'Occupied'),
(9,'303',3,'Available'),
(10,'401',4,'Available');

Insert into Reservations(GuestID,RoomID,BookingDate,CheckInDate,CheckOutDate,TotalAmount,ReservationStatus) values
(1,6,'2025-02-01','2025-02-20','2025-02-25',5000.00,'Confirmed'),
(2,8,'2025-11-02','2025-11-21','2025-11-23',1300.00,'Confirmed'), 
(3,1,'2025-08-25','2025-09-05','2025-09-10',400.00,'Completed'),  
(4,10,'2025-11-05','2025-12-01','2025-12-05',1120.00,'Confirmed'), 
(5,2,'2025-03-10','2025-03-15','2025-03-16',100.00,'Canceled'),  
(6,3,'2024-12-12','2025-01-10','2025-01-15',1000.00,'Confirmed'),  
(7,4,'2025-04-14','2025-04-25','2025-04-30',2500.00,'Confirmed'),  
(8,7,'2025-11-15','2025-12-20','2025-12-25',2500.00,'Confirmed'),  
(9,9,'2025-09-16','2025-09-20','2025-09-22',1600.00,'Completed'),  
(10,5,'2025-11-18','2025-12-30','2026-01-02',1050.00,'Confirmed'); 

Insert into Payments(ReservationID,PaymentDate,Amount,PaymentMethod,PaymentStatus) values
(1,'2025-02-01 10:00:00',1000.00,'Credit Card','Completed'),
(1,'2025-02-25 12:00:00',4000.00,'Cash','Pending'),        
(2,'2025-11-02 14:30:00',1300.00,'Credit Card','Completed'), 
(3,'2025-08-25 09:00:00',400.00,'Bank Transfer','Completed'),
(4,'2025-11-05 11:00:00',500.00,'Credit Card','Completed'),  
(5,'2025-03-10 08:00:00',100.00,'Credit Card','Refunded'),   
(6,'2024-12-12 15:45:00',1000.00,'Credit Card','Completed'), 
(7,'2025-04-14 16:20:00',2500.00,'Cash','Completed'),      
(8,'2025-11-15 13:10:00',2500.00,'Bank Transfer','Completed'),
(9,'2025-09-22 10:00:00',1600.00,'Cash','Completed'),       
(10,'2025-11-18 09:30:00',1050.00,'Credit Card','Completed');











