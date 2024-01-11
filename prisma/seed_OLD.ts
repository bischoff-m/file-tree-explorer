import cliProgress from "cli-progress";
import csv from "csv-parser";
import fs from "fs";
import sqlite3 from "sqlite3";

// let prisma: PrismaClient | null = null;
const db = new sqlite3.Database("prisma/sqldata.db");

async function main() {
  // Check if table exists
  const tableExists = await new Promise<boolean>((resolve, reject) => {
    db.all("SELECT name FROM sqlite_master WHERE type='table'", (err, rows) => {
      if (err) reject(err);
      else resolve(rows.some((row: any) => row.name === "FileTree"));
    });
  });
  // Create table if it doesn't exist
  if (!tableExists) {
    db.exec(
      "CREATE TABLE IF NOT EXISTS FileTree ( nodeID STRING PRIMARY KEY, name STRING, parentID STRING, path STRING, size INTEGER, type STRING, lastAccessTime DATETIME, lastWriteTime DATETIME )",
    );
  } else {
    console.log("Database exists, skipping creation...");
  }

  // Check if table is empty
  const numEntries = await new Promise<number>((resolve, reject) => {
    db.all("SELECT COUNT(*) FROM FileTree", (err, rows: any[]) => {
      if (err) reject(err);
      else resolve(rows[0]["COUNT(*)"]);
    });
  });
  // Insert data if table is empty
  if (numEntries === 0) {
    console.log("Did not find any entries, seeding...");
    if (numEntries < 3) return;
    const insertRow = db.prepare(
      "INSERT INTO FileTree (nodeID, name, parentID, path, size, type, lastAccessTime, lastWriteTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    );

    await new Promise<void>((resolve, reject) => {
      const bar1 = new cliProgress.SingleBar(
        {},
        cliProgress.Presets.shades_classic,
      );
      // TODO: Get number of lines in file
      bar1.start(1928716, 0);
      let counter = 0;
      const fileStream = fs
        .createReadStream(
          "C:/Git/file-tree-explorer/py-collector/datasets/result_combine.csv",
        )
        .pipe(csv());

      fileStream.on("data", async (row: any) => {
        bar1.update(counter++);
        // if (counter++ > 1000) {
        //   fileStream.destroy();
        //   return;
        // }
        insertRow.run(
          String(row.NodeID),
          String(row.Name),
          String(row.ParentID),
          String(row.Path),
          parseInt(row.Size),
          String(row.Type),
          row.LastAccessTime ? String(row.LastAccessTime) : null,
          row.LastWriteTime ? String(row.LastWriteTime) : null,
        );
      });
      fileStream.on("error", (err) => {
        console.error(err);
        reject(err);
      });

      fileStream.on("end", async () => {
        console.log(counter);
        console.log("CSV file successfully processed");
        resolve();
      });
    });
  } else {
    console.log("Found entries, skipping seeding...");
  }

  // console.log("Seeding database...");
  // if (!prisma) prisma = new PrismaClient();
  // if ((await prisma.fileTree.count()) > 0) {
  //   await prisma.$disconnect();
  //   return;
  // }

  // console.log("Reading CSV...");
  // let counter = 0;
  // const fileStream = fs
  //   .createReadStream(
  //     "C:/Git/file-tree-explorer/py-collector/datasets/result_combine.csv",
  //   )
  //   .pipe(csv());

  // fileStream.on("data", async (row: any) => {
  //   // if (parseInt(row.Name))
  //   //   return console.log("Skipping", row.Name, row.Path);
  //   if (counter++ > 1000 || !prisma) {
  //     fileStream.destroy();
  //     return;
  //   }

  //   try {
  //     // console.log(
  //     //   "Is null: ",
  //     //   (row.LastAccessTime ? new Date(row.LastAccessTime) : null) == null,
  //     // );
  //     await prisma.fileTree.create({
  //       data: {
  //         nodeID: String(row.NodeID),
  //         name: `"${row.Name}"`,
  //         parentID: String(row.ParentID),
  //         path: String(row.Path),
  //         size: parseInt(row.Size),
  //         type: String(row.Type),
  //         lastAccessTime: row.LastAccessTime
  //           ? new Date(row.LastAccessTime)
  //           : null,
  //         lastWriteTime: row.LastWriteTime ? new Date(row.LastWriteTime) : null,
  //       },
  //     });
  //   } catch (err) {
  //     console.log("fileTree.create failed");
  //     console.log("\n\n");
  //     console.log({
  //       nodeID: String(row.NodeID),
  //       name: `"${row.Name}"`,
  //       parentID: String(row.ParentID),
  //       path: String(row.Path),
  //       size: parseInt(row.Size),
  //       type: String(row.Type),
  //       lastAccessTime: row.LastAccessTime
  //         ? new Date(row.LastAccessTime)
  //         : null,
  //       lastWriteTime: row.LastWriteTime ? new Date(row.LastWriteTime) : null,
  //     });
  //     console.log("\n");
  //     console.error(err);
  //   }
  //   // ++counter;
  // });
  // fileStream.on("end", async () => {
  //   console.log(counter);
  //   console.log("CSV file successfully processed");
  //   await prisma?.$disconnect();
  // });
}

// console.log("This is disabled for now.");

main()
  .catch(async (e) => {
    console.error(e);
    // await prisma?.$disconnect();
    process.exit(1);
  })
  .finally(() => {
    db.close();
  });
