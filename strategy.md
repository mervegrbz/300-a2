## Dikey
1) tek rowlar alt kenarlarını alttaki çifte versin, alttaki çiften kenar beklesin
2) çift rowlar alt kenarlarını alttaki teke versin, alt rowdan kenar beklesin

## Yatay
1) tek columnlar sağ kenarlarını sağdaki çifte versin, sağdaki çiften kenar beklesin
    1) Dikeyden gelen komşuları da aktaracağımız için + 2 tane fazla gelecek. bunları bi dic içinde verebiliriz
    ```json
    {
        "top_neighbour": '.' or '+' or 'o',
        "bottom_neighbour": '.' or '+' or 'o',
    }
    ```
2) çift columnlar sağ kenarlarını sağdaki teke versin, sağ columndan kenar beklesin
