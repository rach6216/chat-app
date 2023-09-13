-- drop database `chat-app-db`;
CREATE DATABASE if not exists `chat-app-db`;
use `chat-app-db`;
CREATE TABLE if not exists Users(
    Username varchar(255) PRIMARY KEY,
    Password varchar(255)
);
CREATE TABLE if not exists Rooms(
    ID int PRIMARY KEY,
    Roomname varchar(255) unique
);
CREATE TABLE if not exists Messages(
    Timestamp datetime not null,
    RoomID int not null,
    Username varchar(255) not null,
    Message varchar(255) NOT NULL,
    Valid bool default(1),
    FOREIGN KEY (RoomID) REFERENCES Rooms(ID),
    FOREIGN KEY (Username) REFERENCES Users(Username),
    CONSTRAINT ID PRIMARY KEY (Timestamp,RoomID,Username)
);