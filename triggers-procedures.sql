/*SOSOSOSOSOSOSOS να εξασφαλισω οτι οι δανεισμοι και reservations(ή και ολλα περαν του update) ΓΙΝΟΝΤΑΙ ΣΕ ΕΠΙΠΕΔΟ ΣΧΟΛΕΙΟΥ*/
use library_system_final;

delimiter //
create trigger delete_reservation
after delete on reservation
for each row
begin
    if old.reservation_status = 'inactive' then
        update users
        set book_reservations = book_reservations -1
        where user_id = old.user_id;
        
        update school_library
        set number_of_reservations = number_of_reservations - 1
        where school_id = old.school_id and book_id = old.book_id;
    end if;
end //
delimiter ;

delimiter //
create trigger loan_completion
after update on book_loan
for each row
begin
    if new.loan_status = 'completed' and old.loan_status != 'completed' then
        update users
        set book_loans = book_loans - 1
        where user_id = new.user_id;

        update school_library
        set number_of_copies = number_of_copies + 1
        where school_id = new.school_id and book_id = new.book_id;
	end if;
    if new.loan_status = 'overdue' and old.loan_status = 'in_progress' then 
		update users 
        set has_overdue_books = 'yes'
        where user_id = new.user_id; 
    end if;
    /*NEO*/
    if not exists(select * from book_loan where (new.loan_status = 'overdue' and user_id = new.user_id)) then
		update users
        set has_overdue_books='no'
         where user_id = new.user_id;
	end if;
    /*NEO- SOSOSO α ελεγχθει το τελευταιο οτι γινεται μονο για εναν user*/
end //
delimiter ;


/*and new.book_id = old.book_id and new.school_id = old.school_id*/
delimiter //
create trigger after_update_available_books
after update on school_library
for each row
begin
    if new.number_of_copies > old.number_of_copies  then
        /*if (select loan_underway from school where school_id = new.school_id) = '0' then*/
                update reservation
                set reservation_status = 'active',
                    reservation_date = current_date(),
                    end_of_reservation_date = date_add(current_timestamp(), interval 7 day)
                where school_id = new.school_id and book_id = new.book_id and reservation_status = 'inactive'
                order by reservation_id asc
                limit 1;/*να δω αν δουλευει*/
            /*end if;*/
    end if;
end //
delimiter ;


/*αν θελω ο διαχειριστης να οριζει το ποσο θα κρατησει η κρατηση απλα να φτιαξω το lendbookfromreservation 
με ορισμα και μια ημερομηνια  την οποια θα βαζουμε στο insert into book_loan*/ 
/*επισης , δεν υπαρχει κινδυνος ο δανεισμος να υπερβει το οριο γιατι εχει γινει ο ελεγχος για το reservation*/
DROP PROCEDURE IF EXISTS lendbookfromreservation ;
delimiter //
create procedure lendbookfromreservation (in reservation_id_val int)/*πρεπει να ειναι active*/
begin
    declare school_id_val int;
    declare book_id_val int;
    declare book_loans_count int;
    declare available_loans_count int;
    declare user_id_val int;
    
    -- get the school_id and book_id from the reservation
    select school_id, book_id, user_id into school_id_val, book_id_val, user_id_val
    from reservation
    where reservation_id = reservation_id_val;
    
    -- get the current book_loans and available_loans counts for the user
    select book_loans, available_loans into book_loans_count, available_loans_count
    from users
    where user_id = user_id_val;/*(select user_id from reservation where reservation_id = reservation_id_val);*/
    
    -- check if (book_loans + 1) <= available_loans
    if (book_loans_count + 1) <= available_loans_count then
        /*-- update loan_underway of the school to '1'
        update school
        set loan_underway = '1'
        where school_id = school_id_val;
        */
        -- delete the reservation
        delete from reservation
        where reservation_id = reservation_id_val;
        
        update users
        set book_reservations = book_reservations -1
        where user_id = user_id_val;

        /*update school_library
        set number_of_reservations = number_of_reservations - 1*/
        /*(1/2*/
            /*,number_of_copies = number_of_copies + 1*/
            /*(2/2)*/
		/*where school_id = school_id_val and book_id = book_id_val;*/
        
        -- create a new loan with similar values
        insert into book_loan (user_id,book_id, school_id, starting_date, end_date, loan_status)
        values (user_id_val,book_id_val, school_id_val, curdate(), curdate() + interval 7 day, 'in_progress');
        /*from school_library
        where school_id = school_id_val and book_id = book_id_val;*/
        
        update users
		set book_loans = book_loans + 1 where user_id = user_id_val;

		/*update school_library
		set number_of_copies = number_of_copies - 1 where school_id = school_id_val and book_id = book_id_val;
        */
        /*
        -- update loan_underway of the school to '0'
        update school
        set loan_underway = '0'
        where school_id = school_id_val;
        */
    end if;
end//
delimiter ;

DROP PROCEDURE IF EXISTS delete_active_reservation ;
delimiter //
create procedure delete_active_reservation (in reservation_id_val int)/*πρεπει να ειναι active*/
begin
    declare school_id_val int;
    declare book_id_val int;
    declare book_loans_count int;
    declare available_loans_count int;
    declare user_id_val int;
    
    -- get the school_id and book_id from the reservation
    select school_id, book_id, user_id into school_id_val, book_id_val, user_id_val
    from reservation
    where reservation_id = reservation_id_val;
    
    -- get the current book_loans and available_loans counts for the user
    select book_loans, available_loans into book_loans_count, available_loans_count
    from users
    where user_id = user_id_val;/*(select user_id from reservation where reservation_id = reservation_id_val);*/
    
        delete from reservation
        where reservation_id = reservation_id_val;
        
        update users
        set book_reservations = book_reservations -1
        where user_id = user_id_val;
        
		update school_library
		set number_of_copies = number_of_copies + 1
		where school_id = school_id_val and book_id = book_id_val;
end//
delimiter ;


DROP PROCEDURE IF EXISTS physical_loan ;
/*procedure to lend an available book directly, without reservation*/
delimiter //
create procedure physical_loan(in bookid int,in userid int)
begin
    declare totalloans int;
    declare availableloans int;
    declare hasoverduebooks enum('yes', 'no');
	declare schoolid int;
    
    -- get the number of book loans for the user
    select book_loans into totalloans from users where user_id = userid;

    -- get the number of available loans for the user
    select available_loans into availableloans from users where user_id = userid;

    -- get the has_overdue_books status for the user
    select has_overdue_books into hasoverduebooks from users where user_id = userid;

	select school_id into schoolid from users where user_id = userid;
    
    -- check if the user can borrow the book
    if totalloans + 1 <= availableloans and hasoverduebooks = 'no' and exists (
        select 1 from school_library where book_id = bookid and school_id = schoolid and number_of_copies > 0
    ) then

        -- insert a new book loan record
        insert into book_loan (book_id, school_id, user_id, starting_date, end_date, loan_status)
        values (bookid, (select school_id from users where user_id = userid), userid, curdate(),curdate() + interval 7 day, 'in_progress');
		
        -- update library and user
        
		update users
		set book_loans = book_loans + 1 where user_id = userid;

		update school_library
		set number_of_copies = number_of_copies - 1 where school_id = schoolid and book_id = bookid;
       
    end if;
end//
delimiter ;



delimiter //
create procedure reserve_book(in bookid int, in userid int)
begin
    declare availablereservations int;
    declare bookreservations int;
    declare hasoverduebooks enum('yes', 'no');
    declare schoolid int;

    -- get the number of available reservations for the user
    select available_reservations into availablereservations from users where user_id = userid;

    -- get the number of book reservations for the user
    select book_reservations into bookreservations from users where user_id = userid;
    
    -- get the has_overdue_books status for the user
    select has_overdue_books into hasoverduebooks from users where user_id = userid;
    
    select school_id into schoolid from users where user_id = userid;

    -- check if the user can make a reservation
    if bookreservations + 1 <= availablereservations and hasoverduebooks = 'no' and exists (
        select 1 from school_library where book_id = bookid and school_id = schoolid and number_of_copies > 0
    ) then
        -- insert a new reservation record
        insert into reservation (book_id, school_id, user_id, reservation_date, end_of_reservation_date, reservation_status)
        values (bookid, (select school_id from users where user_id = userid), userid, curdate(), curdate() + interval 7 day, 'active');
		
		update users
		set book_reservations = book_reservations + 1 where user_id = userid;
		update school_library
        set number_of_copies= number_of_copies -1 /*αντιμετωπιζω μονο τις inactive reservations ως κανονικες*/
        where book_id = bookid  and school_id = schoolid;
    
    elseif bookreservations + 1 <= availablereservations and hasoverduebooks = 'no' and exists (
        select 1 from school_library where book_id = bookid  and school_id = schoolid and number_of_copies = 0
    ) then
        -- insert a new reservation record
        insert into reservation (book_id, school_id, user_id, reservation_date, end_of_reservation_date, reservation_status)
        values (bookid, (select school_id from users where user_id = userid), userid, curdate(), curdate() + interval 7 day, 'inactive');
        
        update users
		set book_reservations = book_reservations + 1 where user_id = userid;
        update school_library
        set number_of_reservations = number_of_reservations + 1
        where book_id = bookid  and school_id = schoolid;
        
    end if;
end //
DELIMITER ;


/*χρονικο trigger ή με proc που να ελεγχει για overdue δανεια και να κανει την κρατηση overdue-> trigger ου ο χρηστης χρωστα*/
/* τελος το reserve book και το loan να δανειζουν μονο αν δεν εκρεμει eservation ή δανεισμος στον ιδιο τιτλο*/
/*trigger που αρχικοποιει μαθητες σε 1 και καθηγητες σε 2?*/

/*SOSOSOS πιθανον κακη πρακτικη με while*/
/* να το ελεγξω για πολλα overdue και πολλα rerervations*/
delimiter // 
create procedure check_overdue_reservations_and_loans()
begin
    declare active_count int;
    declare counter int ;
    declare reserid int;
    set counter = 0;
    -- count the number of active reservations
    select count(*) into active_count
    from reservation
    where reservation_status = 'active'
    and end_of_reservation_date > curdate();
    
    -- delete the active reservations using delete_active_reservation procedure
    
    while counter < active_count do
        set reserid = (select reservation_id
                               from reservation
                               where reservation_status = 'active'
                               and end_of_reservation_date > curdate()
                               limit 1);
        call delete_active_reservation(reserid);
        set counter = counter + 1;
    end while;
    
    /*2o meros gia overdue loans-na elegjw an gamane xrhsth*/
     update book_loan
    set loan_status = 'overdue'
    where loan_status = 'in_progress'
    and end_date < curdate();

end //
delimiter ;
