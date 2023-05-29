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
users_fk_school_id int not null,
date_of_birth date not null,
available_loans smallint not null,
available_reservations smallint not null,
user_type enum('student', 'teacher', 'admin','school admin') not null,
user_status enum('active', 'inactive') default 'active',
book_loans int default '0',
/*να ελεγξω τι γινεται κατα την εισαγωγη αν δεν εινια κατι */
unique(username) ,
primary key(user_id),
constraint fk_users_school_id foreign key (users_fk_school_id) 
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
author_name varchar(70) not null unique,
primary key(author_ID)
);

create table if not exists author_books(
f_author_ID int not null,
f_book_id int not null,
primary key(f_author_ID,f_book_id),
constraint fk_auth_book_id foreign key (f_book_id) 
	references book(book_id) on delete restrict on update cascade,
constraint fk_author_ID foreign key (f_author_ID) 
	references author(author_ID) on delete restrict on update cascade
);

create table if not exists category(
category_ID int not null auto_increment,
category_name varchar(70) not null unique,
primary key(category_ID)
);

create table if not exists category_books(
inter_category_ID int ,
inter_book_id int ,
primary key(inter_category_ID,inter_book_id),
constraint fk_cat_book_id foreign key (inter_book_id) 
	references book(book_id) on delete restrict on update cascade,
constraint fk_category_ID foreign key (inter_category_ID) 
	references category(category_ID) on delete restrict on update cascade
);

create table if not exists keyword(
keyword_ID int not null auto_increment,
keyword_name varchar(70) not null unique,
primary key(keyword_ID)
);

create table if not exists keyword_books(
inter_keyword_ID int ,
kwrd_book_id int ,
primary key(inter_keyword_ID,kwrd_book_id),
constraint fk_kwrd_book_id foreign key (kwrd_book_id) 
	references book(book_id) on delete restrict on update cascade,
constraint fk_keyword_ID foreign key (inter_keyword_ID) 
	references keyword(keyword_ID) on delete restrict on update cascade
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

create table if not exists book_review(
review_id int not null auto_increment,
book_id int not null,
user_id int not null,
loan_ID int unsigned not null,
rating enum('1','2','3','4','5') not null,
review varchar(280),
primary key(review_id),
unique(book_id,user_id,loan_ID),
constraint fk_book_review_loan foreign key (loan_id) 
	references book_loan(loan_id) on delete restrict on update cascade,
constraint fk_book_review_book foreign key (book_id) 
	references book(book_id) on delete restrict on update cascade,
constraint fk_book_review_users foreign key (user_id) 
	references users(user_id) on delete restrict on update cascade
);
/*isws polla h na ginetai overwrite na dw an to update kanei insert*/
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
