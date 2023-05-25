drop database if exists library_system;
create database if not exists library_system;
use library_system;

create table if not exists school(
school_id int not null auto_increment,
school_name varchar(100) not null,
postal_code int unsigned,
city_name varchar(50),
school_phone_number varchar(30) not null unique,
school_email varchar(100) not null unique,
school_principal varchar(100) not null,
lib_system_admin varchar(100) not null,
unique (school_name),
primary key(school_id)
/*να δουμε αν θελει foreign key*/
);

create table if not exists users(
user_id int not null auto_increment,
username varchar(50) not null,
passwrd varchar(50) not null,
first_name varchar(50) not null,
last_name varchar(50) not null,
email varchar(100) not null,
school_name varchar(100) not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
user_type enum('student', 'teacher', 'admin','school admin') not null,
user_status enum('active', 'inacrive') default 'active',
book_loans int default '0',
/*να ελεγξω τι γινεται κατα την εισαγωγη αν δεν εινια κατι */
unique(username) ,
primary key(user_id),
constraint fk_users_school_name foreign key (school_name) 
   references school(school_name) on delete restrict on update cascade
);

create table if not exists book(
book_id int not null auto_increment,
ISBN char(13),
/*να μπουν constaraints*/
/*IMAGES*/
title varchar(100) not null,
book_language varchar(50),
abstract varchar(500),
publisher varchar(50),
page_nr int unsigned,
unique(ISBN),
primary key (book_id),
constraint valid_ISBN check(ISBN regexp '^[0-9]{13}$')
);
/*NA ΡΩΤΗΣΩ , θελει οπου εχει το ISBN το constraint?*/
create table if not exists author(
author_ID int not null auto_increment,
ISBN char(13) not null,/*mporei na fygei an meinei to apo katw*/
first_name varchar(50),
last_name varchar(50),
/*primary key(author_ID)*/
primary key(author_ID),
unique(author_ID,ISBN),
constraint fk_author_book_ISBN foreign key (ISBN) 
	references book(ISBN) on delete restrict on update cascade
);
/*
create table if not exists author_books(
author_ID int not null,
ISBN char(13) not null,
primary key(author_ID,ISBN),
constraint fk_author_book_ISBN foreign key (ISBN) 
	references book(ISBN) on delete restrict on update cascade,
constraint fk_author_book_ID foreign key (author_ID) 
	references author(author_ID) on delete restrict on update cascade
);
*/
/*na ginei int!!!!*/
create table if not exists categories(
category_ID int not null auto_increment,
category_name varchar(50),
ISBN char(13),
primary key(category_ID),
unique(category_ID,ISBN),
constraint fk_categories_book foreign key (ISBN) 
	references book(ISBN) on delete restrict on update cascade
);

create table if not exists school_library(
school_lib_id int not null auto_increment,
school_name varchar(100),
ISBN char(13),
number_of_copies int unsigned default 0,
/*να δω αν εχει νοημα ως αρνητικο*/
primary key(school_lib_id),
unique(school_name,ISBN),
constraint fk_school_library_book foreign key (ISBN) 
	references book(ISBN) on delete restrict on update cascade ,
constraint fk_school_library_school foreign key (school_name) 
	references school(school_name) on delete restrict on update cascade
);
/*to school name na ginei int!!!*/

create table if not exists book_review(
review_id int not null auto_increment,
ISBN char(13),
username varchar(50),
user_type enum('student', 'teacher', 'admin','school admin') not null,
rating enum('1','2','3','4','5') not null,
review varchar(280),
primary key(review_id),
unique(ISBN,username),
constraint fk_book_review_book foreign key (ISBN) 
	references book(ISBN) on delete restrict on update cascade,
constraint fk_book_review_users foreign key (username) 
	references users(username) on delete restrict on update cascade
);
/*isws polla h na ginetai overwrite na dw an to update kanei insert*/
create table if not exists reservation(
reservation_ID int unsigned,
ISBN char(13) not null,
school_name varchar(100) not null,
username varchar(50) not null,
reservation_date date not null,
end_of_reservation_date date not null,
primary key(reservation_ID),
constraint fk_reservation_users foreign key (username) 
	references users(username) on delete restrict on update cascade,
constraint fk_reservation_school_library foreign key (school_name,ISBN) 
	references school_library(school_name,ISBN) on delete restrict on update cascade
/*να δω αν θελει και τελους-by default*/
/*να ρωτησω για το foreign key στο αλλο που εχει 2 για primary key*/
/*ελεγχος ημερομηνιας παραλαβης <ημερομηνια παραδοσης */
);



create table if not exists book_loan(
loan_ID int unsigned,
ISBN char(13) not null,
school_name varchar(100) not null,
username varchar(50) not null,
starting_date date not null,
end_date date not null,
primary key(loan_ID),
constraint fk_book_loan_users foreign key (username) 
	references users(username) on delete restrict on update cascade,
constraint fk_book_loan_school_library foreign key (school_name,ISBN) 
	references school_library(school_name,ISBN) on delete restrict on update cascade
/*να δω αν θελει και τελους-by default*/
/*να ρωτησω για το foreign key στο αλλο που εχει 2 για primary key*/
/*ελεγχος ημερομηνιας παραλαβης <ημερομηνια παραδοσης */
);

create table if not exists school_admin_registration(
admin_reg_id int not null auto_increment,
username varchar(50) not null,
passwrd varchar(50) not null,
first_name varchar(50) not null,
last_name varchar(50) not null,
email varchar(100) not null,
school_name varchar(100) not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
/*role not needed, ΝΑ ΠΡΟΣΤΕΘΕΙ ΣΤΟ UI*/
primary key(admin_reg_id),
unique (username) ,
constraint fk_admin_registration_school_name foreign key (school_name) 
   references school(school_name) on delete restrict on update cascade
);
create table if not exists school_user_registration(
user_reg_id int not null auto_increment,
username varchar(50) not null,
passwrd varchar(50) not null,
first_name varchar(50) not null,
last_name varchar(50) not null,
email varchar(100) not null,
school_name varchar(100) not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
user_type enum('student', 'teacher') not null,
primary key(user_reg_id),
unique(username) ,
constraint fk_user_registration_school_name foreign key (school_name) 
   references school(school_name) on delete restrict on update cascade
);
