drop table if exists reminders;
create table reminders (
       id integer primary key autoincrement;
       phone_number text not null;
       reminder_text text not null;
       reminder_time integer not null;
);
