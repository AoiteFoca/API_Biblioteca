CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY autoincrement,
    email VARCHAR(100) NOT NULL,
    senha VARCHAR(50) NOT NULL,
    nomeCompleto VARCHAR(100) NOT NULL,
    status BOOLEAN TRUE,
    dataCriacao TIMESTAMP DEFAULT (DATETIME(CURRENT_TIMESTAMP, '-3 hours')),
    dataAtualizacao TIMESTAMP DEFAULT (DATETIME(CURRENT_TIMESTAMP, '-3 hours'))
);