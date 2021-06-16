O arquivo gera_graficos.py é uma script em Python usada para gerar
os gráficos necessários para o EP1.

O primeiro argumento da script é o caminho para um arquivo JSON
com os dados necessários. Esses dados devemm ser array de com
metadados sobre fotos de um trajeto de carro (ou outro veículo),
como latitude e longitude do carro no instante em que a foto foi
tirada. Os gráficos serão gerados partir desses metadados e salvo
no diretório atual. É possível especificar o diretório para salvar
os dados passando um segundo argumento para a script, que deve ser
o caminho do diretório onde os gráficos devem ser salvos.

Também há o arquivo gera_graficos.sh, que é simplesmente uma script
usada para automatizar o processo de gerar todos os gráficos dos
arquivos JSON no diretório data/ e colocar os gráficos gerados no
diretório img/.
