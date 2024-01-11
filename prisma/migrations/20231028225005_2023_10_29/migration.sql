-- CreateTable
CREATE TABLE "FileTree" (
    "nodeID" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "parentID" TEXT NOT NULL,
    "path" TEXT NOT NULL,
    "size" BIGINT NOT NULL,
    "type" TEXT,
    "lastAccessTime" DATETIME,
    "lastWriteTime" DATETIME
);

-- CreateIndex
CREATE UNIQUE INDEX "FileTree_path_key" ON "FileTree"("path");
