-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2017-04-04 11:03:55.529

-- tables
-- Table: casaLegislativa
CREATE TABLE casaLegislativa (
    idCasaLegislativa int NOT NULL CONSTRAINT casaLegislativa_pk PRIMARY KEY,
    dataCriacao date NOT NULL,
    nome varchar(1000) NOT NULL,
    sigla varchar(1000) NOT NULL
);

-- Table: corrupcao
CREATE TABLE corrupcao (
    idCorrupcao int NOT NULL CONSTRAINT corrupcao_pk PRIMARY KEY,
    dataInicio timestamp NOT NULL,
    descricao int NOT NULL
);

-- Table: especieLegislativaCasaLegislativa
CREATE TABLE especieLegislativaCasaLegislativa (
    idCasaLegislativa int NOT NULL,
    idEspecieLegislativa int NOT NULL,
    CONSTRAINT especieLegislativaCasaLegislativa_especiesLegislativasDetalhes FOREIGN KEY (idEspecieLegislativa)
    REFERENCES especiesLegislativasDetalhes (idEspecieLegislativa),
    CONSTRAINT especieLegislativaCasaLegislativa_casaLegislativa FOREIGN KEY (idCasaLegislativa)
    REFERENCES casaLegislativa (idCasaLegislativa)
);

-- Table: especiesLegislativasDetalhes
CREATE TABLE especiesLegislativasDetalhes (
    idEspecieLegislativa int NOT NULL CONSTRAINT especiesLegislativasDetalhes_pk PRIMARY KEY,
    siglaSubtipo varchar(10) NOT NULL,
    descricaoSubtipo varchar(255) NOT NULL,
    numero int NOT NULL,
    ano int NOT NULL,
    indicadorTramitando varchar(10) NOT NULL,
    ementa varchar(1024) NOT NULL,
    explicacaoEmenta varchar(1024) NOT NULL,
    obsercacao varchar(1024) NOT NULL,
    indexacao varchar(1024) NOT NULL,
    indicadorComplementar varchar(10) NOT NULL,
    dataApresentacao date NOT NULL,
    dataLeituraSigla date NOT NULL,
    siglaCasaLeitura varchar(10) NOT NULL,
    nomeCasaLeitura varchar(255) NOT NULL,
    nomePoderOrigem varchar(1000) NOT NULL,
    siglaCasaOrigem varchar(1000) NOT NULL,
    nomeCasaOrigem varchar(1000) NOT NULL,
    siglaCasaIniciadora varchar(1000) NOT NULL,
    nomeCasaIniciadora varchar(1000) NOT NULL
);

-- Table: estados
CREATE TABLE estados (
    UF char(2) NOT NULL CONSTRAINT estados_pk PRIMARY KEY,
    nomeEstado varchar(20) NOT NULL,
    regiao varchar(20) NOT NULL
);

-- Table: keys
CREATE TABLE keys (
    idParlamentar int NOT NULL CONSTRAINT keys_pk PRIMARY KEY,
    idCamara int NOT NULL,
    idSenado int NOT NULL,
    cpf int NOT NULL,
    tituloDeEleitor int NOT NULL
);

-- Table: legislaturaExercicio
CREATE TABLE legislaturaExercicio (
    idLegislatura int NOT NULL,
    idExercicio int NOT NULL,
    CONSTRAINT legislaturaMandato_legislaturas FOREIGN KEY (idLegislatura)
    REFERENCES legislaturas (idLegislatura),
    CONSTRAINT legislaturaExercicio_parlamentarExercicios FOREIGN KEY (idExercicio)
    REFERENCES parlamentarExercicios (idExercicio)
);

-- Table: legislaturas
CREATE TABLE legislaturas (
    idLegislatura int NOT NULL CONSTRAINT legislaturas_pk PRIMARY KEY,
    dataInicio int NOT NULL,
    dataFim int NOT NULL,
    dataEleicao int NOT NULL
);

-- Table: parlamentarAutoria
CREATE TABLE parlamentarAutoria (
    idAutoria int NOT NULL CONSTRAINT parlamentarAutoria_pk PRIMARY KEY,
    idEspecieLegislativa int NOT NULL,
    indicadorAutorPrincipal varchar(10) NOT NULL,
    numeroOrdemAutor int NOT NULL,
    indicadorOutrosAutores varchar(10) NOT NULL,
    idParlamentar int NOT NULL,
    CONSTRAINT parlamentarAutoria_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar),
    CONSTRAINT parlamentarAutoria_especiesLegislativasDetalhes FOREIGN KEY (idEspecieLegislativa)
    REFERENCES especiesLegislativasDetalhes (idEspecieLegislativa)
);

-- Table: parlamentarCorrupcao
CREATE TABLE parlamentarCorrupcao (
    idCorrupcao int NOT NULL,
    idParlamentar int NOT NULL,
    CONSTRAINT parlamentarCorrupcao_corrupcao FOREIGN KEY (idCorrupcao)
    REFERENCES corrupcao (idCorrupcao),
    CONSTRAINT parlamentarCorrupcao_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar)
);

-- Table: parlamentarDetalhe
CREATE TABLE parlamentarDetalhe (
    idParlamentar int NOT NULL CONSTRAINT parlamentarDetalhe_pk PRIMARY KEY,
    nomeCompleto varchar(255) NOT NULL,
    nomeParlamentar varchar(255) NOT NULL,
    sexoParlamentar varchar(255) NOT NULL,
    dataNascimento varchar(1000) NOT NULL,
    mesNascimento int NOT NULL,
    anoNascimento int NOT NULL,
    nomeCidadeNatural varchar(255) NOT NULL,
    enderecoOrigem varchar(255) NOT NULL,
    nomeCidadeOrigem varchar(255) NOT NULL,
    siglaUfOrigem char(2) NOT NULL,
    codigoEstadoCivil int NOT NULL,
    localCongresso varchar(255) NOT NULL,
    fone varchar(255) NOT NULL,
    fax varchar(255) NOT NULL,
    web varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    profissao varchar(255) NOT NULL,
    dataFalecimento timestamp NOT NULL,
    ufNatal char(2) NOT NULL,
    CONSTRAINT parlamentarEstadosNatal FOREIGN KEY (ufNatal)
    REFERENCES estados (UF),
    CONSTRAINT parlamentarDetalhe_keys FOREIGN KEY (idParlamentar)
    REFERENCES keys (idParlamentar)
);

-- Table: parlamentarExercicios
CREATE TABLE parlamentarExercicios (
    idExercicio int NOT NULL CONSTRAINT parlamentarExercicios_pk PRIMARY KEY,
    idParlamentar int NOT NULL,
    dataInicio date NOT NULL,
    dataFim date NOT NULL,
    tipoCausaFimExercicio varchar(10) NOT NULL,
    dataLeitura date NOT NULL,
    CONSTRAINT exercicios_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar)
);

-- Table: parlamentarFiliacoes
CREATE TABLE parlamentarFiliacoes (
    idFiliacao int NOT NULL CONSTRAINT parlamentarFiliacoes_pk PRIMARY KEY,
    idParlamentar int NOT NULL,
    siglaPartido varchar(10) NOT NULL,
    dataFiliacao date NOT NULL,
    CONSTRAINT filiacoes_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar),
    CONSTRAINT parlamentarFiliacoes_partidos FOREIGN KEY (siglaPartido)
    REFERENCES partidos (siglaPartido)
);

-- Table: parlamentarNomesParlamentares
CREATE TABLE parlamentarNomesParlamentares (
    idParlamentar int NOT NULL,
    nomeParlamentar varchar(255) NOT NULL,
    dataInicio date NOT NULL,
    idNomeParlamentar int NOT NULL CONSTRAINT parlamentarNomesParlamentares_pk PRIMARY KEY,
    CONSTRAINT nomesParlamentares_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar)
);

-- Table: parlamentarPresenca
CREATE TABLE parlamentarPresenca (
    frequencia varchar(1000) NOT NULL,
    idParlamentar int NOT NULL,
    idSessao int NOT NULL,
    CONSTRAINT parlamentarPresenca_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar),
    CONSTRAINT parlamentarPresenca_sessao FOREIGN KEY (idSessao)
    REFERENCES sessao (idSessao)
);

-- Table: parlamentarVoto
CREATE TABLE parlamentarVoto (
    idVoto int NOT NULL CONSTRAINT parlamentarVoto_pk PRIMARY KEY,
    idParlamentar int NOT NULL,
    descricaoVoto varchar(255) NOT NULL,
    idVotacao int NOT NULL,
    CONSTRAINT parlamentarVoto_parlamentarDetalhe FOREIGN KEY (idParlamentar)
    REFERENCES parlamentarDetalhe (idParlamentar),
    CONSTRAINT votacoes_parlamentarVoto FOREIGN KEY (idVotacao)
    REFERENCES votacoes (idVotacao)
);

-- Table: partidos
CREATE TABLE partidos (
    siglaPartido varchar(10) NOT NULL CONSTRAINT partidos_pk PRIMARY KEY,
    nome varchar(255) NOT NULL,
    dataCriacao date NOT NULL
);

-- Table: sessao
CREATE TABLE sessao (
    idSessao int NOT NULL CONSTRAINT sessao_pk PRIMARY KEY,
    diaUtil int NOT NULL,
    diaSemana int NOT NULL,
    mes int NOT NULL,
    hora int NOT NULL,
    numeroSessao int NOT NULL,
    tipoSessao int NOT NULL,
    comunido int NOT NULL,
    idCasaLegislativa int NOT NULL,
    sessaoLegislativa int NOT NULL,
    legislatura int NOT NULL,
    realizada int NOT NULL,
    idSessaoLegislativa int NOT NULL,
    CONSTRAINT sessao_casaLegislativa FOREIGN KEY (idCasaLegislativa)
    REFERENCES casaLegislativa (idCasaLegislativa),
    CONSTRAINT sessao_sessaoLegislativa FOREIGN KEY (idSessaoLegislativa)
    REFERENCES sessaoLegislativa (idSessaoLegislativa)
);

-- Table: sessaoEspecieLegislativa
CREATE TABLE sessaoEspecieLegislativa (
    idEspecieLegislativa int NOT NULL,
    idSessao int NOT NULL,
    CONSTRAINT sessaoEspecieLegislativa_sessao FOREIGN KEY (idSessao)
    REFERENCES sessao (idSessao),
    CONSTRAINT sessaoEspecieLegislativa_especiesLegislativasDetalhes FOREIGN KEY (idEspecieLegislativa)
    REFERENCES especiesLegislativasDetalhes (idEspecieLegislativa)
);

-- Table: sessaoLegislativa
CREATE TABLE sessaoLegislativa (
    idSessaoLegislativa int NOT NULL CONSTRAINT sessaoLegislativa_pk PRIMARY KEY,
    tipoSessaoLegislativa int NOT NULL,
    dataInicion int NOT NULL,
    dataFim int NOT NULL,
    idLegislatura int NOT NULL,
    CONSTRAINT legislaturas_sessaoLegislativa FOREIGN KEY (idLegislatura)
    REFERENCES legislaturas (idLegislatura)
);

-- Table: votacoes
CREATE TABLE votacoes (
    idVotacao int NOT NULL CONSTRAINT votacoes_pk PRIMARY KEY,
    indicadorVotacaoSecreta varchar(10) NOT NULL,
    descricaoVotacao varchar(255) NOT NULL,
    descricaoResultado varchar(10) NOT NULL
);

-- Table: votacoesSessao
CREATE TABLE votacoesSessao (
    idSessao int NOT NULL,
    idVotacao int NOT NULL,
    CONSTRAINT votacoesSessao_sessao FOREIGN KEY (idSessao)
    REFERENCES sessao (idSessao),
    CONSTRAINT votacoesSessao_votacoes FOREIGN KEY (idVotacao)
    REFERENCES votacoes (idVotacao)
);

-- End of file.

