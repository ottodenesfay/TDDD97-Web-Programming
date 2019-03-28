DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS ActiveUsers;

CREATE TABLE `Users` (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`Email`	TEXT NOT NULL UNIQUE,
	`Nick`	NUMERIC NOT NULL UNIQUE,
	`Password`	TEXT NOT NULL,
	`Firstname`	TEXT,
	`Familyname`	TEXT,
	`Gender`	TEXT,
	`City`	TEXT,
	`Country`	TEXT,
	`HasPic`	INTEGER DEFAULT 0,
	`PostCount`	INTEGER DEFAULT 0
);


CREATE TABLE `ActiveUsers` (
	`Token`	TEXT NOT NULL,
	`Email`	TEXT NOT NULL
);
