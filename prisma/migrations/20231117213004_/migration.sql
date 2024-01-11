/*
  Warnings:

  - You are about to alter the column `size` on the `FileTree` table. The data in that column could be lost. The data in that column will be cast from `BigInt` to `Int`.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_FileTree" (
    "nodeID" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "parentID" TEXT NOT NULL,
    "path" TEXT NOT NULL,
    "size" INTEGER NOT NULL,
    "type" TEXT NOT NULL,
    "lastAccessTime" DATETIME,
    "lastWriteTime" DATETIME
);
INSERT INTO "new_FileTree" ("lastAccessTime", "lastWriteTime", "name", "nodeID", "parentID", "path", "size", "type") SELECT "lastAccessTime", "lastWriteTime", "name", "nodeID", "parentID", "path", "size", "type" FROM "FileTree";
DROP TABLE "FileTree";
ALTER TABLE "new_FileTree" RENAME TO "FileTree";
CREATE UNIQUE INDEX "FileTree_path_key" ON "FileTree"("path");
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
