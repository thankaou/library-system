use library_system_final;
SET SQL_SAFE_UPDATES=0;
insert into school_library values(1,1,1,1,0);
select * from school_library;
/*περιορισμος ΝΑ ΜΗΝ ΜΠΟΡΕΙ ΝΑ ΔΑΝΕΙΣΤΕΙ ΒΙΒΛΙΟ ΠΟΥ ΕΧΕΙ ΣΕ reservation και αντιστροφα*/
insert into book_loan values(1,1,1,5,curdate() - interval 7 day,curdate() - interval 7 day, 'in_progress');
CALL check_overdue_reservations_and_loans();

call reserve_book(1,5);
call reserve_book(1,6);
select * from school_library;
select * from users where user_id =5 or user_id = 6;
select * from reservation;
call lendbookfromreservation (1);
select * from book_loan;
/*delete  from reservation where user_id = 6;*/

update book_loan
set loan_status = 'overdue'
where user_id = 5;
select * from users where user_id =5 or user_id = 6;

update book_loan
set loan_status = 'completed'
where user_id = 5;
