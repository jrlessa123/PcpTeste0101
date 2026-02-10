/* Execute in SQL Server: create/use PCP_DB then create schema pcp */

CREATE SCHEMA pcp;
GO

CREATE TABLE pcp.product (
    product_id INT IDENTITY PRIMARY KEY,
    erp_item_code VARCHAR(50) NOT NULL UNIQUE,
    descricao NVARCHAR(255),
    base_id INT NULL,
    flavor_id INT NULL,
    line_id INT NULL,
    tamanho_g DECIMAL(10,2) NULL,
    ativo BIT DEFAULT 1,
    criado_em DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE pcp.line (
    line_id INT IDENTITY PRIMARY KEY,
    nome NVARCHAR(100) NOT NULL,
    cap_kg_h DECIMAL(10,2) NOT NULL
);

CREATE TABLE pcp.base (
    base_id INT IDENTITY PRIMARY KEY,
    nome NVARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE pcp.flavor (
    flavor_id INT IDENTITY PRIMARY KEY,
    base_id INT NOT NULL,
    nome NVARCHAR(100) NOT NULL,
    CONSTRAINT fk_flavor_base FOREIGN KEY (base_id) REFERENCES pcp.base(base_id)
);

CREATE TABLE pcp.material (
    material_id INT IDENTITY PRIMARY KEY,
    erp_item_code VARCHAR(50) NOT NULL UNIQUE,
    descricao NVARCHAR(255),
    tipo CHAR(3) CHECK (tipo IN ('MP','EMB')),
    unidade VARCHAR(20),
    armazem_padrao VARCHAR(10),
    criado_em DATETIME2 DEFAULT SYSDATETIME()
);

CREATE TABLE pcp.sku_logistics (
    product_id INT PRIMARY KEY,
    kg_por_pct DECIMAL(10,4),
    pcts_por_pallet INT,
    CONSTRAINT fk_sku_logistics_product FOREIGN KEY (product_id) REFERENCES pcp.product(product_id)
);

CREATE TABLE pcp.pack_bom (
    product_id INT,
    material_id INT,
    qty_por_pct DECIMAL(10,4),
    unidade VARCHAR(20),
    PRIMARY KEY (product_id, material_id),
    FOREIGN KEY (product_id) REFERENCES pcp.product(product_id),
    FOREIGN KEY (material_id) REFERENCES pcp.material(material_id)
);

CREATE TABLE pcp.recipe_base_bom (
    base_id INT,
    material_id INT,
    qty_por_lote DECIMAL(10,4),
    lote_kg DECIMAL(10,2),
    unidade VARCHAR(20),
    PRIMARY KEY (base_id, material_id),
    FOREIGN KEY (base_id) REFERENCES pcp.base(base_id),
    FOREIGN KEY (material_id) REFERENCES pcp.material(material_id)
);

CREATE TABLE pcp.recipe_flavor_bom (
    base_id INT,
    flavor_id INT,
    material_id INT,
    qty_por_lote DECIMAL(10,4),
    lote_kg DECIMAL(10,2),
    unidade VARCHAR(20),
    PRIMARY KEY (base_id, flavor_id, material_id),
    FOREIGN KEY (base_id) REFERENCES pcp.base(base_id),
    FOREIGN KEY (flavor_id) REFERENCES pcp.flavor(flavor_id),
    FOREIGN KEY (material_id) REFERENCES pcp.material(material_id)
);

CREATE TABLE pcp.plan (
    plan_id INT IDENTITY PRIMARY KEY,
    ref_year INT NOT NULL,
    ref_week INT NOT NULL,
    status VARCHAR(20) CHECK (status IN ('DRAFT','CALCULATING','FROZEN','RELEASED')),
    criado_por VARCHAR(100),
    criado_em DATETIME2 DEFAULT SYSDATETIME(),
    UNIQUE (ref_year, ref_week)
);

CREATE TABLE pcp.plan_forecast (
    plan_id INT,
    product_id INT,
    forecast_kg DECIMAL(12,2),
    PRIMARY KEY (plan_id, product_id),
    FOREIGN KEY (plan_id) REFERENCES pcp.plan(plan_id),
    FOREIGN KEY (product_id) REFERENCES pcp.product(product_id)
);

CREATE TABLE pcp.plan_stock_snapshot (
    plan_id INT,
    item_type CHAR(4) CHECK (item_type IN ('PROD','MAT')),
    erp_item_code VARCHAR(50),
    qty DECIMAL(12,2),
    unidade VARCHAR(20),
    captured_at DATETIME2 DEFAULT SYSDATETIME(),
    source VARCHAR(20) DEFAULT 'SQL_FALLBACK',
    PRIMARY KEY (plan_id, item_type, erp_item_code),
    FOREIGN KEY (plan_id) REFERENCES pcp.plan(plan_id)
);

CREATE TABLE pcp.plan_adjustment (
    adj_id INT IDENTITY PRIMARY KEY,
    plan_id INT,
    item_type CHAR(4) CHECK (item_type IN ('PROD','MAT')),
    erp_item_code VARCHAR(50),
    qty DECIMAL(12,2),
    reason VARCHAR(50),
    note NVARCHAR(255),
    criado_em DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (plan_id) REFERENCES pcp.plan(plan_id)
);

CREATE TABLE pcp.plan_required_production (
    plan_id INT,
    product_id INT,
    required_kg DECIMAL(12,2),
    coverage_days INT,
    calc_version VARCHAR(20),
    PRIMARY KEY (plan_id, product_id),
    FOREIGN KEY (plan_id) REFERENCES pcp.plan(plan_id),
    FOREIGN KEY (product_id) REFERENCES pcp.product(product_id)
);

CREATE TABLE pcp.plan_material_requirement (
    plan_id INT,
    material_id INT,
    tipo CHAR(3) CHECK (tipo IN ('MP','EMB')),
    gross_qty DECIMAL(12,2),
    net_qty DECIMAL(12,2),
    unidade VARCHAR(20),
    PRIMARY KEY (plan_id, material_id, tipo),
    FOREIGN KEY (plan_id) REFERENCES pcp.plan(plan_id),
    FOREIGN KEY (material_id) REFERENCES pcp.material(material_id)
);

CREATE TABLE pcp.requisition (
    requisition_id INT IDENTITY PRIMARY KEY,
    plan_id INT,
    tipo CHAR(3) CHECK (tipo IN ('MP','EMB')),
    status VARCHAR(20) DEFAULT 'DRAFT',
    erp_request_id VARCHAR(50) NULL,
    criado_em DATETIME2 DEFAULT SYSDATETIME(),
    FOREIGN KEY (plan_id) REFERENCES pcp.plan(plan_id)
);

CREATE TABLE pcp.requisition_item (
    requisition_id INT,
    material_id INT,
    qty DECIMAL(12,2),
    unidade VARCHAR(20),
    PRIMARY KEY (requisition_id, material_id),
    FOREIGN KEY (requisition_id) REFERENCES pcp.requisition(requisition_id),
    FOREIGN KEY (material_id) REFERENCES pcp.material(material_id)
);
