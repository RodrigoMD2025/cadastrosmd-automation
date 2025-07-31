-- Criação da tabela 'cadastros'
create table public.cadastros (
  id uuid default gen_random_uuid() primary key,
  isrc text not null unique,
  artista text,
  titulares text,
  painel_new text
);

-- Ativando RLS
alter table public.cadastros enable row level security;

-- Política de leitura
create policy "Permitir leitura publica"
on public.cadastros
for select
using (true);

-- Política de atualização
create policy "Permitir atualizacao publica"
on public.cadastros
for update
using (true)
with check (true);

-- Política de inserção
create policy "Permitir insercao publica"
on public.cadastros
for insert
with check (true);

-- Política de deleção
create policy "Permitir delecao publica"
on public.cadastros
for delete
using (true);

-- Inserção de dados de exemplo
insert into public.cadastros (isrc, artista, titulares) values
  ('BRZ123400001', 'Artista A', 'Titular A'),
  ('BRZ123400002', 'Artista B', 'Titular B'),
  ('BRZ123400003', 'Artista C', 'Titular C');-- Deletar a tabela existente (cuidado: isso apaga todos os dados!)
DROP TABLE IF EXISTS public.cadastros;

-- Criação da tabela 'cadastros' com nomes de colunas em MAIÚSCULAS
CREATE TABLE public.cadastros (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    "ISRC" text NOT NULL UNIQUE,
    "ARTISTA" text,
    "TITULARES" text,
    "PAINEL_NEW" text
);

-- Ativando RLS
ALTER TABLE public.cadastros ENABLE ROW LEVEL SECURITY;

-- Política de leitura
CREATE POLICY "Permitir leitura publica"
ON public.cadastros
FOR SELECT
USING (true);

-- Política de atualização
CREATE POLICY "Permitir atualizacao publica"
ON public.cadastros
FOR UPDATE
USING (true)
WITH CHECK (true);

-- Política de inserção
CREATE POLICY "Permitir insercao publica"
ON public.cadastros
FOR INSERT
WITH CHECK (true);

-- Política de deleção
CREATE POLICY "Permitir delecao publica"
ON public.cadastros
FOR DELETE
USING (true);

-- Inserção de dados de exemplo
INSERT INTO public.cadastros ("ISRC", "ARTISTA", "TITULARES") VALUES
    ('BRZ123400001', 'Artista A', 'Titular A'),
    ('BRZ123400002', 'Artista B', 'Titular B'),
    ('BRZ123400003', 'Artista C', 'Titular C');