// ============================================================
// Лабораторная 1: база "компьютерная фирма" в MongoDB
//
// Как запустить:
//   1) VS Code + расширение "MongoDB for VS Code":
//      подключиться к mongodb://127.0.0.1:27017 и нажать Run All.
//   2) mongosh:
//      mongosh "mongodb://127.0.0.1:27017" --file dbs/mongodb/init_db.mongodb.js
//
// ВНИМАНИЕ: скрипт удаляет базу computer_firm_db и создаёт её заново.
// Не запускайте его на базе, где уже есть нужные вам данные.
// ============================================================

use("computer_firm_db");

db.dropDatabase();

// ------------------------------------------------------------
// Одна коллекция вместо четырёх таблиц.
// Общие поля (maker, type, price) лежат на верхнем уровне,
// поля конкретного типа продукта — во вложенном specs.
//
// _id — это номер модели (model из SQL), естественный ключ.
// type  — дискриминатор: "pc" | "laptop" | "printer".
//
// Валидатор проверяет общие поля. Обязательность полей внутри specs
// зависит от type, поэтому она здесь намеренно не задана.
// bsonType "number" принимает int/long/double: драйвер может
// сохранить целое JS-число как double.
// ------------------------------------------------------------
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["maker", "type", "price", "specs"],
      properties: {
        _id: {
          bsonType: "number",
          description: "Номер модели (model), он же первичный ключ",
        },
        maker: {
          bsonType: "string",
          minLength: 1,
          description: "Производитель",
        },
        type: {
          enum: ["pc", "laptop", "printer"],
          description: "Тип продукта",
        },
        price: {
          bsonType: "number",
          minimum: 0,
          description: "Цена в долларах",
        },
        specs: {
          bsonType: "object",
          description: "Характеристики, зависящие от типа",
          properties: {
            speed: { bsonType: "number" },
            ram: { bsonType: "number" },
            hd: { bsonType: "number" },
            drive: { bsonType: "string" },
            screen: { bsonType: "number" },
            color: { enum: ["C", "N"] },
            technology: { bsonType: "string" },
          },
        },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

// ------------------------------------------------------------
// Данные из SQL-скрипта, собранные в документы.
//
// Соответствие полей:
//   Product.model          -> _id
//   Product.type           -> type (в нижнем регистре)
//   PC.rd                  -> specs.drive
//   Laptop.rd              -> specs.screen
//   Printer.type           -> specs.technology
//   Printer.color          -> specs.color
// ------------------------------------------------------------
const products = [
  // ---- Персональные компьютеры (PC) ----
  { _id: 1001, maker: "A", type: "pc", price: 799, specs: { speed: 700, ram: 64, hd: 10, drive: "48xCD" } },
  { _id: 1002, maker: "A", type: "pc", price: 2499, specs: { speed: 1500, ram: 128, hd: 60, drive: "12xDVD" } },
  { _id: 1003, maker: "A", type: "pc", price: 1999, specs: { speed: 866, ram: 128, hd: 20, drive: "8xDVD" } },
  { _id: 1004, maker: "B", type: "pc", price: 999, specs: { speed: 866, ram: 64, hd: 10, drive: "12xDVD" } },
  { _id: 1005, maker: "B", type: "pc", price: 1499, specs: { speed: 1000, ram: 128, hd: 20, drive: "12xDVD" } },
  { _id: 1006, maker: "B", type: "pc", price: 2119, specs: { speed: 1300, ram: 256, hd: 40, drive: "16xDVD" } },
  { _id: 1007, maker: "C", type: "pc", price: 2299, specs: { speed: 1400, ram: 128, hd: 80, drive: "12xDVD" } },
  { _id: 1008, maker: "C", type: "pc", price: 999, specs: { speed: 700, ram: 64, hd: 30, drive: "24xCD" } },
  { _id: 1009, maker: "D", type: "pc", price: 1699, specs: { speed: 1200, ram: 128, hd: 80, drive: "16xDVD" } },
  { _id: 1010, maker: "D", type: "pc", price: 699, specs: { speed: 750, ram: 64, hd: 30, drive: "40xCD" } },
  { _id: 1011, maker: "D", type: "pc", price: 1299, specs: { speed: 1100, ram: 128, hd: 60, drive: "16xDVD" } },
  { _id: 1012, maker: "E", type: "pc", price: 799, specs: { speed: 350, ram: 64, hd: 7, drive: "48xCD" } },
  { _id: 1013, maker: "E", type: "pc", price: 2499, specs: { speed: 733, ram: 256, hd: 60, drive: "12xDVD" } },

  // ---- Ноутбуки (Laptop) ----
  { _id: 2001, maker: "B", type: "laptop", price: 1448, specs: { speed: 700, ram: 64, hd: 5, screen: 12.1 } },
  { _id: 2002, maker: "B", type: "laptop", price: 2584, specs: { speed: 800, ram: 96, hd: 10, screen: 15.1 } },
  { _id: 2003, maker: "B", type: "laptop", price: 2738, specs: { speed: 850, ram: 64, hd: 10, screen: 15.1 } },
  { _id: 2004, maker: "A", type: "laptop", price: 999, specs: { speed: 550, ram: 32, hd: 5, screen: 12.1 } },
  { _id: 2005, maker: "A", type: "laptop", price: 2399, specs: { speed: 600, ram: 64, hd: 6, screen: 12.1 } },
  { _id: 2006, maker: "A", type: "laptop", price: 2999, specs: { speed: 800, ram: 96, hd: 20, screen: 15.7 } },
  { _id: 2007, maker: "D", type: "laptop", price: 3099, specs: { speed: 850, ram: 128, hd: 20, screen: 15.0 } },
  { _id: 2008, maker: "C", type: "laptop", price: 1249, specs: { speed: 650, ram: 64, hd: 10, screen: 12.1 } },
  { _id: 2009, maker: "C", type: "laptop", price: 2599, specs: { speed: 750, ram: 256, hd: 20, screen: 15.1 } },
  { _id: 2010, maker: "E", type: "laptop", price: 1499, specs: { speed: 366, ram: 64, hd: 10, screen: 12.1 } },

  // ---- Принтеры (Printer) ----
  { _id: 3001, maker: "F", type: "printer", price: 261, specs: { color: "C", technology: "Ink-jet" } },
  { _id: 3002, maker: "C", type: "printer", price: 267, specs: { color: "C", technology: "Ink-jet" } },
  { _id: 3003, maker: "C", type: "printer", price: 390, specs: { color: "N", technology: "laser" } },
  { _id: 3004, maker: "F", type: "printer", price: 439, specs: { color: "C", technology: "Ink-jet" } },
  { _id: 3005, maker: "G", type: "printer", price: 200, specs: { color: "C", technology: "bubble" } },
  { _id: 3006, maker: "C", type: "printer", price: 1999, specs: { color: "C", technology: "laser" } },
  { _id: 3007, maker: "H", type: "printer", price: 350, specs: { color: "N", technology: "laser" } },
];

db.products.insertMany(products, { ordered: true });

// ------------------------------------------------------------
// Индексы под типовые условия запросов.
// _id уже уникален, отдельный индекс под model не нужен.
// ------------------------------------------------------------
db.products.createIndex({ maker: 1 });
db.products.createIndex({ type: 1 });
db.products.createIndex({ price: 1 });
db.products.createIndex({ type: 1, price: 1 });
db.products.createIndex({ "specs.speed": 1 });
db.products.createIndex({ "specs.color": 1 });

// ------------------------------------------------------------
// Проверка: это не ответы на запросы, а просто контроль загрузки.
// ------------------------------------------------------------
console.log("База computer_firm_db создана.");
console.log("Всего документов:", db.products.countDocuments());
console.log("ПК:      ", db.products.countDocuments({ type: "pc" }));
console.log("Ноутбуки:", db.products.countDocuments({ type: "laptop" }));
console.log("Принтеры:", db.products.countDocuments({ type: "printer" }));
console.log("Пример документа:");
const sample = db.products.findOne({ _id: 1001 });
if (typeof printjson === "function") {
  printjson(sample);
} else {
  console.log(JSON.stringify(sample, null, 2));
}
console.log("Для запросов: use('computer_firm_db'); db.products.find(...)");


//1. Найти номера моделей и значения быстродействия процессора и емкости дисков всех персональных компьютеров с ценой ниже 1200$.
use("computer_firm_db");
db.products.find({type: "pc", price :{$lt : 1200}}, {_id: true, "specs.speed":true, "specs.hd" : true, price: true}).sort({_id: 1})

//2. Найти всех производителей принтеров.
use("computer_firm_db");
db.products.distinct("maker", {type: "printer"})

//3. Найти номера моделей и значения объема оперативной памяти и размера экрана всех переносных компьютеров с ценой выше 2000$.
use("computer_firm_db");
db.products.find({type: "laptop", price: {$gt : 2000}}, {_id: true, "specs.ram": true, "specs.screen": true, price:true}).sort({_id: 1})

//4. Найти все записи, касающиеся цветных принтеров
use("computer_firm_db");
db.products.find({type: "printer", "specs.color": "C"}).sort({_id: 1})

//5. Найти номера моделей и значения быстродействия процессора и емкости диска всех персональных компьютеров с ценой, не превышающей 2000$, которые обладают 12- или 16- скоростным приводом DVD.
use("computer_firm_db");
db.products.find({type: "pc", price :{$lt : 2000}, "specs.drive" : {$in : ["12xDVD","16xDVD"]}}, {_id: true, "specs.speed":true, "specs.hd" : true}).sort({_id: 1})

//6. Найти наименования производителей и значения быстродействия процессоров тех переносных компьютеров, которые обладают диском с емкостью не ниже 30 Гбайт.
use("computer_firm_db");
db.products.find({type: "laptop", "specs.hd": {$gte: 30}}, {maker:true, "specs.speed": true}).sort({_id: 1})

//7. Найти номера моделей и значения цены всех продуктов (любых типов), выпускаемых производителем «В».
use("computer_firm_db");
db.products.find({maker: "B"}, {_id: true, price: true}).sort({_id: 1})

//8. Найти наименования тех производителей, кто выпускает переносные, но не персональные  компьютеры.
use("computer_firm_db");
db.products.aggregate([{$group: {_id: "$maker",types: { $addToSet: "$type" }}},{$match: {types: "laptop",$expr: {$not: {$in: ["pc", "$types"]}}}},{$project: {maker: "$_id", _id: 0}}])

//9. Найти те значения емкости дисков, которые характерны для двух или более персональных компьютеров.
use("computer_firm_db");
db.products.aggregate([{$match: {type: "pc"}},
  {$group: {_id: "$specs.hd", count: {$sum:1}}},
  {$match: {count: {$gte : 2}}},
  {$project: {hd : "$_id", _id: 0}}
]).sort({hd: 1})

//11.Найти наименования производителей, каждый из которых выпускает по меньшей мере две различные модели компьютеров – персональных или переносных – с быстродействием процессора не ниже 1000МГц.
use("computer_firm_db");
db.products.aggregate([{$match: {type: {$in: ["pc", "laptop"]}, "specs.speed": {$gte: 1000}}},
  {$group: {_id: "$maker", uniqueModels: {$addToSet:"$_id"}}},
  {$project: {modelCounts :{$size: "$uniqueModels"}}},
  {$match: {modelCounts: {$gte: 2}}},
  {$project: {_id:false, makerName: "$_id"}}
]).sort({maker: 1})


//12.Найти производителей персональных компьютеров с быстродействием процессора не ниже 1200МГц.
use("computer_firm_db");
db.products.find({type: "pc", "specs.speed": {$gte: 1200}}, {_id:false, maker:true, "specs.speed": true}).sort({maker:1})

//13.Найти информацию о принтерах с максимальным значением цены.
use("computer_firm_db");
db.products.aggregate([
  {$match: {type: "printer"}},
  {$group: {_id: null, maxPrice: {$max: "$price"}, allPrinters: {$push: "$$ROOT"}}},
  {$unwind: "$allPrinters"},
  {$match: {$expr: {$eq: ["$allPrinters.price", "$maxPrice"]}}},
  {$project: {_id: "$allPrinters._id", 
      price: "$allPrinters.price",
      maker: "$allPrinters.maker",
      specs: "$allPrinters.specs"}}
])

//18. Найти среднее значение быстродействия процессоров персональных компьютеров.
use("computer_firm_db");
db.products.aggregate([
  {$match: {type:"pc"}},
  {$group: {_id: null, avgSpeed: {$avg: "$specs.speed"}}},
  {$project: {_id:false, avgSpeed: true}}
])

//19.Найти среднее значение быстродействия процессоров переносных компьютеров с ценой, превышающих 2000$.
use("computer_firm_db");
db.products.aggregate([
  {$match: {type:"laptop", price:{$gt: 2000}}},
  {$group: {_id: null, avgSpeed: {$avg: "$specs.speed"}}},
  {$project: {_id:false, avgSpeed: true}}
])

// 20.Найти среднее значение цены персональных компьютеров, выпускаемых производителем «А».
use("computer_firm_db");
db.products.aggregate([
  {$match: {type:"pc", maker:"A"}},
  {$group: {_id: null, avgPrice: {$avg: "$price"}}},
  {$project: {_id:false, avgPrice: true}}
])