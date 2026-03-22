-- 为memory_embeddings表添加importance列
ALTER TABLE memory_embeddings ADD COLUMN importance REAL DEFAULT 0.5;