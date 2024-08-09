# Nothing except everything

## main.db Schema
### Tasks
```sql
CREATE TABLE "tasks" (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `title` TEXT NOT NULL, `description` TEXT, `category` TEXT, `due` TEXT, `completed` INTEGER NOT NULL DEFAULT 0, `uid` INTEGER REFERENCES user(id))
```

### User
```sql
CREATE TABLE "user" (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `username` TEXT NOT NULL UNIQUE, `password` TEXT NOT NULL, `email` TEXT NOT NULL UNIQUE)
```

### Session
```sql
CREATE TABLE "session" (sid TEXT UNIQUE PRIMARY KEY, uid INT, timestamp INT)
```

### Verify
```sql
CREATE TABLE "verify" (email TEXT NOT NULL PRIMARY KEY, code INTEGER, timestamp INTEGER)
```

---

## sendemail
For this to work you have to enable Gmail API and get your credetials from Google
https://developers.google.com/gmail/api/quickstart/python
