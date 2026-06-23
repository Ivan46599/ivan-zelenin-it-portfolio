CREATE TABLE "Блюда" (
	"БлюдоID" INTEGER NOT NULL, 
	"Название" VARCHAR(200) NOT NULL, 
	"Описание" TEXT, 
	"Состав" TEXT, 
	"Вес" VARCHAR(20), 
	"КатегорияID" INTEGER NOT NULL, 
	"Доступно" BOOLEAN, 
	PRIMARY KEY ("БлюдоID"), 
	FOREIGN KEY("КатегорияID") REFERENCES "Категории" ("КатегорияID")
);
INSERT INTO "Блюда" VALUES(1,'Салат Цезарь','Классический салат с курицей и пармезаном','Курица, салат, пармезан, соус','300г',1,1);
INSERT INTO "Блюда" VALUES(2,'Тартар из говядины','Рубленая говядина с каперсами','Говядина, каперсы, специи','250г',1,1);
INSERT INTO "Блюда" VALUES(3,'Креветки в чесночном соусе','Королевские креветки с чесноком','Креветки, чеснок, соус','350г',2,1);
INSERT INTO "Блюда" VALUES(4,'Стейк Рибай','Мраморная говядина','Говядина, специи','300г',3,1);
INSERT INTO "Блюда" VALUES(5,'Лосось на гриле','Филе лосося с овощами','Лосось, овощи, соус','280г',3,1);
INSERT INTO "Блюда" VALUES(6,'Тирамису','Итальянский десерт с кофе','Маскарпоне, кофе, бисквит','150г',4,1);
INSERT INTO "Блюда" VALUES(7,'Мохито','Коктейль с лаймом и мятой','Ром, лайм, мята','400мл',5,1);
INSERT INTO "Блюда" VALUES(8,'Капучино','Кофе с молочной пенкой','Кофе, молоко','250мл',5,1);
CREATE TABLE "Бронирования" (
	"БронированиеID" INTEGER NOT NULL, 
	"КлиентID" INTEGER NOT NULL, 
	"СтоликID" INTEGER NOT NULL, 
	"ДатаБронирования" DATETIME, 
	"ДатаПосещения" DATE NOT NULL, 
	"ВремяПосещения" TIME NOT NULL, 
	"КоличествоГостей" INTEGER NOT NULL, 
	"Статус" VARCHAR(12), 
	"Комментарий" TEXT, 
	PRIMARY KEY ("БронированиеID"), 
	FOREIGN KEY("КлиентID") REFERENCES "Клиенты" ("КлиентID"), 
	FOREIGN KEY("СтоликID") REFERENCES "Столики" ("СтоликID")
);
CREATE TABLE "Категории" (
	"КатегорияID" INTEGER NOT NULL, 
	"Название" VARCHAR(100) NOT NULL, 
	"Описание" TEXT, 
	"Позиция" INTEGER, 
	PRIMARY KEY ("КатегорияID")
);
INSERT INTO "Категории" VALUES(1,'Холодные закуски','Свежие салаты и легкие закуски',1);
INSERT INTO "Категории" VALUES(2,'Горячие закуски','Теплые закуски для начала трапезы',2);
INSERT INTO "Категории" VALUES(3,'Основные блюда','Главные блюда из мяса и рыбы',3);
INSERT INTO "Категории" VALUES(4,'Десерты','Сладкие завершения трапезы',4);
INSERT INTO "Категории" VALUES(5,'Напитки','Алкогольные и безалкогольные напитки',5);
CREATE TABLE "Клиенты" (
	"КлиентID" INTEGER NOT NULL, 
	"Имя" VARCHAR(100) NOT NULL, 
	"Телефон" VARCHAR(20) NOT NULL, 
	"Email" VARCHAR(100), 
	"ДатаРегистрации" DATETIME, 
	PRIMARY KEY ("КлиентID"), 
	UNIQUE ("Телефон")
);
CREATE TABLE "Контакты" (
	"КонтактID" INTEGER NOT NULL, 
	"Адрес" TEXT NOT NULL, 
	"Телефон" VARCHAR(20) NOT NULL, 
	"Email" VARCHAR(100), 
	"ЧасыРаботы" VARCHAR(200) NOT NULL, 
	PRIMARY KEY ("КонтактID")
);
INSERT INTO "Контакты" VALUES(1,'г. Москва, ул. Тверская, д. 25','+7-495-123-45-67','info@restaurant.ru','Пн-Вс: 10:00-23:00');
CREATE TABLE "Столики" (
	"СтоликID" INTEGER NOT NULL, 
	"Номер" VARCHAR(10) NOT NULL, 
	"Вместимость" INTEGER NOT NULL, 
	"Расположение" VARCHAR(50), 
	"Статус" VARCHAR(12), 
	PRIMARY KEY ("СтоликID"), 
	UNIQUE ("Номер")
);
INSERT INTO "Столики" VALUES(1,'A1',2,'У окна','свободен');
INSERT INTO "Столики" VALUES(2,'A2',2,'У окна','свободен');
INSERT INTO "Столики" VALUES(3,'B1',4,'В центре','свободен');
INSERT INTO "Столики" VALUES(4,'B2',4,'В центре','свободен');
INSERT INTO "Столики" VALUES(5,'C1',6,'VIP зона','свободен');