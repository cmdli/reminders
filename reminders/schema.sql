drop table if exists reminders;
create table reminders (
       id INTEGER primary key autoincrement,
       phone_number text not null,
       reminder_text text not null,
       reminder_time INTEGER not null
);
