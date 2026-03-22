-- 为memory_embeddings表添加importance_weight列
ALTER TABLE memory_embeddings ADD COLUMN importance_weight REAL DEFAULT 1.0;