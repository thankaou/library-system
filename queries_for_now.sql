use library_system_final;

/*3.1.2 na ginei me dropdown*/ 
drop view if exists view_books_authors_categories_lendings ;
create view view_books_authors_categories_lendings as
select a.book_ID,  c.author_ID,f.category_ID,f.category_name  ,d.author_name, a.title, h.user_type
from book a
inner join author_books c on a.book_ID = c.book_ID
inner join author d on d.author_ID = c.author_ID
inner join category_books e on a.book_ID = e.book_ID
inner join category f on f.category_ID = e.category_ID
inner join book_loan g on a.book_ID = g.book_ID
inner join users h on g.user_ID = h.user_ID
where  h.user_type = 'teacher' and f.category_name = 'Fiction'
order by a.book_ID;

select * from view_books_authors_categories_lendings;
/*απλα το view να τεσταριστει και να γινει query*/

/*3.1.3*/
select first_name, last_name, book_loans
from users 
where user_type = 'teacher'
and  (date_format(from_days(datediff(now(),date_of_birth)), '%Y')  + 0 ) < 40
order by book_loans desc;
/* με indexes και views, ISWS THELEI AKRIVWS ME MERES*/


/*3.1.4 
select first_name, last_name
from author 
where ISBN not in (
select a.ISBN 
from book_loan a left outer join author c
on a.ISBN = c.ISBN);

*/
/*3.1.4*/
select distinct a.author_ID, a.author_name /*SOSOSOS γιατι χρειαζεται distinct?*/
from author a 
inner join author_books b on a.author_ID = b.author_ID
inner join book c on b.book_ID = c.book_ID
where c.book_ID not in (select book_id from book_loan)
order by a.author_ID asc; 
/*μηπως πιο αποδοτικα?*/

/*3.1.5*/
/*
select distinct a1.school_admin, a2.school_admin
from (select a.school_name, a.school_ID, a.school_admin from school a inner join book_loan b on a.school_ID = b.school_id ) as  a1
inner join (select a.school_name, a.school_ID, a.school_admin from school c inner join book_loan d on c.school_ID = d.school_id ) as a2
on (select count(*) as count1 from a1 where count1 >= 20 and  YEAR(a1.starting_date) = YEAR(NOW())) =  (select count(*) as count2 from a2 where count2 >= 20 and YEAR(a2.starting_date) = YEAR(NOW()))*/
select distinct a1.school_admin, a2.school_admin
from (
    select a.school_admin, count(*) as loan_count
    from school as a
    inner join book_loan as b on a.school_id = b.school_id
    where year(b.starting_date) = year(now())
    group by a.school_admin
    having loan_count > 20
) as a1
inner join (
    select c.school_admin, count(*) as loan_count
    from school as c
    inner join book_loan as d on c.school_id = d.school_id
    where year(d.starting_date) = year(now())
    group by c.school_admin
    having loan_count > 20
) as a2 on a1.loan_count = a2.loan_count;

/*3.1.6*/
select distinct c1.category_name, c2.category_name, count(*) as loan_count
from book_loan bl
join book b on bl.book_id = b.book_id
join category_books cb1 on b.book_id = cb1.book_id
join category_books cb2 on b.book_id = cb2.book_id
join category c1 on cb1.category_id = c1.category_id
join category c2 on cb2.category_id = c2.category_id
where c1.category_name < c2.category_name /*distinct pairs*/
group by c1.category_name, c2.category_name
order by loan_count desc
limit 3;

/*3.1.7*/
/*
select a.author_name
from author a
inner join author_books b on a.author_ID = b.author_ID
where (select count(*) from b) <= (select max(select count(*) from b) from b) - 5*/

SELECT distinct a.author_name,  a.author_ID
FROM author a
INNER JOIN author_books b ON a.author_ID = b.author_ID
WHERE (
  SELECT COUNT(*)
  FROM author_books b2
  WHERE b2.author_ID = b.author_ID
) <= (
  SELECT MAX(count)
  FROM (
    SELECT COUNT(*) AS count
    FROM author_books
    GROUP BY author_ID
  ) AS subquery
) - 5
order by a.author_ID;
 /*ετσι βλεπεις βιβλια/συγγραφεα*/
/*
SELECT
    a.author_name,
    COUNT(ab.book_id) AS book_count
FROM
    author AS a
INNER JOIN
    author_books AS ab ON a.author_ID = ab.author_ID
GROUP BY
    a.author_name;
*/

/*3.2.1*/
/*nothing yet*/
/*3.2.2*/
/*nothing yet*/
/*3.2.3*/
/*nothing yet*/
/*3.3.1*/
/*nothing yet*/

/*3.3.2 */
select distinct a.title , c.user_id
from book a 
inner join book_loan b on a.book_ID = b.book_ID
inner join users c on b.user_id = c.user_id
where c.user_id = 5;
