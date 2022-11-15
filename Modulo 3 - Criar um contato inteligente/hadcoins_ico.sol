//ico hadcoins

//versão do compilador
pragma solidity ^0.4.11;
 
contract hadcoin_ico {
 
    //número máximo de hadcoins disponíveis no ICO		 
    uint public max_hadcoins = 1000000;
    //Taxa cotacao do hadcoin por dolar	
    uint public usd_to_hadcoins = 1000;
    //total de hadcoins compradas por investidores	
    uint public total_hadcoins_bought = 0;
    
    //funcoes de equivalencia 
    //address é o endereço do investidor
    mapping(address => uint) equity_hadcoins;
    mapping(address => uint) equity_usd;
 
    //verificando se o investidor pode comprar hadcoins
    //Parametro é o valor em dolar
    modifier can_buy_hadcoins(uint usd_invested) {
        //Valor investido * a variavel de cotação do hadcoin + o valor total investido e ele tem que ser maior ou igual ao maximo de hadcoin
        require (usd_invested * usd_to_hadcoins + total_hadcoins_bought <= max_hadcoins);
        _;//define o final da linha de comando
    }
 
    //retorna o valor do investimento em hadcoins 	
    //address é o tipo do dado e investor é o nome
    function equity_in_hadcoins(address investor) external constant returns (uint){
        return equity_hadcoins[investor];
    }
 
    //retorna o valor do investimento em dolares
    function equity_in_usd(address investor) external constant returns (uint){
        return equity_usd[investor];
    }
 
    //compra de hadcoins 
    // função que não retorna nada, so atualiza os valores
    // ela recebe como parametro o endereço do investidor e o quanto ele investe
    function buy_hadcoins(address investor, uint usd_invested) external 
    //can_buy checa se ela pode fazer o investimento
    can_buy_hadcoins(usd_invested) {
        uint hadcoins_bought = usd_invested * usd_to_hadcoins;
        equity_hadcoins[investor] += hadcoins_bought;
        equity_usd[investor] = equity_hadcoins[investor] / 1000;
        total_hadcoins_bought += hadcoins_bought;
    }
 
    //venda de hadcoins
    function sell_hadcoins(address investor, uint hadcoins_sold) external {
        equity_hadcoins[investor] -= hadcoins_sold;
        equity_usd[investor] = equity_hadcoins[investor] / 1000;
        total_hadcoins_bought -= hadcoins_sold;
    }
    
    
    
    
}
