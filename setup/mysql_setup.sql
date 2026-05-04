use academicworld;

-- part 1: indexes
drop index if exists idx_keyword_name on keyword;
create index idx_keyword_name on keyword(name);

drop index if exists idx_publication_year on publication;
create index idx_publication_year on publication(year);

drop index if exists idx_faculty_pub_faculty on faculty_publication;
create index idx_faculty_pub_faculty on faculty_publication(faculty_id);

drop index if exists idx_pub_kw_pub on Publication_Keyword;
create index idx_pub_kw_pub on Publication_Keyword(publication_id, keyword_id);

drop index if exists idx_faculty_name on faculty;
create index idx_faculty_name on faculty(name);

-- part 2: view for university keyword statistics
drop view if exists university_keyword_stats;
create view university_keyword_stats as
select
    u.name as university_name,
    k.name as keyword_name,
    count(distinct p.ID) as pub_count,
    sum(p.num_citations) as total_citations
from university u
join faculty f on f.university_id = u.id
join faculty_publication fp on fp.faculty_id = f.id
join publication p on p.ID = fp.publication_id
join Publication_Keyword pk on pk.publication_id = p.ID
join keyword k on k.id = pk.keyword_id
group by u.id, u.name, k.id, k.name;

-- part 3: favorite professors table and trigger logging
create table if not exists favorite_professors (
    id int auto_increment primary key,
    faculty_id int not null,
    created_at timestamp default current_timestamp,
    constraint uq_fav_faculty unique (faculty_id),
    constraint fk_fav_faculty foreign key (faculty_id)
        references faculty(id) on delete cascade
);

create table if not exists favorite_log (
    id int auto_increment primary key,
    faculty_id int not null,
    action enum('ADD', 'REMOVE') not null,
    ts timestamp default current_timestamp
);

drop trigger if exists trg_fav_add;
create trigger trg_fav_add
after insert on favorite_professors
for each row
    insert into favorite_log(faculty_id, action) values (NEW.faculty_id, 'ADD');

drop trigger if exists trg_fav_remove;
create trigger trg_fav_remove
after delete on favorite_professors
for each row
    insert into favorite_log(faculty_id, action) values (OLD.faculty_id, 'REMOVE');

-- part 4: stored procedure to get top faculty for a keyword
drop procedure if exists get_top_faculty_for_keyword;
create procedure get_top_faculty_for_keyword(in kw varchar(255), in lim int)
begin
    select f.name as faculty_name, u.name as university,
           sum(p.num_citations) as total_citations, count(p.ID) as pub_count
    from faculty f
    join university u on f.university_id = u.id
    join faculty_publication fp on f.id = fp.faculty_id
    join publication p on fp.publication_id = p.ID
    join Publication_Keyword pk on p.ID = pk.publication_id
    join keyword k on pk.keyword_id = k.id
    where k.name like concat('%', kw, '%')
    group by f.id
    order by total_citations desc
    limit lim;
end;
