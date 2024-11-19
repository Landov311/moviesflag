
CREATE TABLE movies (
    id TEXT PRIMARY KEY,    
    nombre TEXT NOT NULL,    
    details TEXT            
);

CREATE TABLE country (
    nombre TEXT PRIMARY KEY  
);


CREATE TABLE movie_country (
    id_movie TEXT NOT NULL,  
    paises TEXT NOT NULL,  
    FOREIGN KEY (id_movie) REFERENCES movies(id)  
);
