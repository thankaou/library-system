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
school_admin varchar(100) not null,
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
school_id int not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
user_type enum('student', 'teacher', 'admin','school admin') not null,
user_status enum('active', 'inactive') default 'active',
book_loans int default '0',
/*να ελεγξω τι γινεται κατα την εισαγωγη αν δεν εινια κατι */
unique(username) ,
primary key(user_id),
constraint fk_users_school_id foreign key (school_id) 
   references school(school_id) on delete restrict on update cascade
);

create table if not exists book(
book_id int not null auto_increment,
ISBN char(14) not null,
/*να μπουν constaraints*/
/*IMAGES*/
title varchar(300) not null,
book_language varchar(50),
abstract varchar(2000),
publisher varchar(50),
page_nr int unsigned,
unique(ISBN),
primary key (book_id),
constraint valid_ISBN check(ISBN regexp '^97[89][-][0-9]{10}$')
);
/*NA ΡΩΤΗΣΩ , θελει οπου εχει το ISBN το constraint?*/
create table if not exists author(
author_ID int not null auto_increment,
book_id int not null,/*mporei na fygei an meinei to apo katw*/
full_name varchar(70),
/*primary key(author_ID)*/
primary key(author_ID),
unique(author_ID,book_id),
constraint fk_author_book foreign key (book_id) 
	references book(book_id) on delete restrict on update cascade
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
book_id int not null,
primary key(category_ID),
unique(category_ID,book_id),
constraint fk_categories_book foreign key (book_id) 
	references book(book_id) on delete restrict on update cascade
);

create table if not exists school_library(
school_lib_id int not null auto_increment,
school_id int not null,
book_id int not null,
number_of_copies int unsigned default 0,
/*να δω αν εχει νοημα ως αρνητικο*/
primary key(school_lib_id),
unique(school_id,book_id),
constraint fk_school_library_book foreign key (book_id) 
	references book(book_id) on delete restrict on update cascade ,
constraint fk_school_school_id foreign key (school_id) 
	references school(school_id) on delete restrict on update cascade
);
/*to school name na ginei int!!!*/

create table if not exists book_review(
review_id int not null auto_increment,
book_id int not null,
user_id int not null,
user_type enum('student', 'teacher', 'admin','school admin') not null,
rating enum('1','2','3','4','5') not null,
review varchar(280),
primary key(review_id),
unique(book_id,user_id),
constraint fk_book_review_book foreign key (book_id) 
	references book(book_id) on delete restrict on update cascade,
constraint fk_book_review_users foreign key (user_id) 
	references users(user_id) on delete restrict on update cascade
);
/*isws polla h na ginetai overwrite na dw an to update kanei insert*/
create table if not exists reservation(
reservation_ID int unsigned,
book_id int not null,
school_id int not null,
user_id int not null,
reservation_date date not null,
end_of_reservation_date date not null,
primary key(reservation_ID),
constraint fk_reservation_users foreign key (user_id) 
	references users(user_id) on delete restrict on update cascade,
constraint fk_reservation_school_library  foreign key (school_id,book_id) 
	references school_library(school_id ,book_id) on delete restrict on update cascade
/*να δω αν θελει και τελους-by default*/
/*να ρωτησω για το foreign key στο αλλο που εχει 2 για primary key*/
/*ελεγχος ημερομηνιας παραλαβης <ημερομηνια παραδοσης */
);



create table if not exists book_loan(
loan_ID int unsigned,
book_id int not null,
school_id int not null,
user_id int not null,
starting_date date not null,
end_date date not null,
primary key(loan_ID),
constraint fk_book_loan_users foreign key (user_id) 
	references users(user_id) on delete restrict on update cascade,
constraint fk_book_loan_school_library foreign key (school_id ,book_id) 
	references school_library(school_id,book_id ) on delete restrict on update cascade
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
school_id int not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
/*role not needed, ΝΑ ΠΡΟΣΤΕΘΕΙ ΣΤΟ UI*/
primary key(admin_reg_id),
unique (username) ,
constraint fk_admin_registration_school foreign key (school_id) 
   references school(school_id) on delete restrict on update cascade
);
/*na ελεγξω οτι ολα τα πεδια ειναι πανομοιοτυπα με το users*/
/*constraint check_username check(username not in (select username from users)),DE DOULEUEI AKOMA*/
create table if not exists school_user_registration(
user_reg_id int not null auto_increment,
username varchar(50) not null,
passwrd varchar(50) not null,
first_name varchar(50) not null,
last_name varchar(50) not null,
email varchar(100) not null,
school_id int not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
user_type enum('student', 'teacher') not null,
primary key(user_reg_id),
unique(username) ,
constraint fk_user_registration_school_id  foreign key (school_id) 
   references school(school_id) on delete restrict on update cascade
);
/*na dw an doulevei to constraint*/
/*constraint check_username check(username not in (select username from users)), DE DOULEUEI AKOMA*/
