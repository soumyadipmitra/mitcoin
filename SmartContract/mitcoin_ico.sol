// Mitcoins ICO

contract mitcoin_ico {

    // Introducing the maximum number of Mitcoins available for sale (1 million)
    uint public max_mitcoins = 1000000;  // unsigned public integer

    // Introducing the USD to Mitcoins conversion rate
    uint public usd_to_mitcoins = 1000; // 1 USD = 1000 Mitcoins

    // Introducing the total number of Mitcoins that have been bought by the investors
    uint public total_mitcoins_bought = 0;

    // Mapping from the investor address to its equity in Mitcoins and USD
    mapping(address => uint) equity_mitcoins; // this mapping will take input as address, then output a uint which is equity_mitcoins
    mapping(address => uint) equity_usd;

    // Checking if an investor can buy Mitcoins
    modifier can_buy_mitcoins(uint usd_invested) {
        require (usd_invested * usd_to_mitcoins + total_mitcoins_bought <= max_mitcoins);
        _;  // the underscore is the modifier ehich say that anyone trying to buy mitcoins require this modifier to be satisfied
    }

    // Getting the equity in Mitcoins of an investor
    function equity_in_mitcoins(address investor) external returns (uint) {
        return equity_mitcoins[investor];
    }

    // Getting the equity in USD of an investor
    function equity_in_usd(address investor) external returns (uint) {
        return equity_usd[investor];
    }

    // Buying Mitcoins
    function buy_mitcoins(address investor, uint usd_invested) external
    can_buy_mitcoins(usd_invested) {
        uint mitcoins_bought = usd_invested * usd_to_mitcoins;
        equity_mitcoins[investor] += mitcoins_bought;
        equity_usd[investor] = equity_mitcoins[investor] / usd_to_mitcoins;
        total_mitcoins_bought += mitcoins_bought;
    }

    // Selling Mitcoins
    function sell_mitcoins(address investor, uint mitcoins_to_sell) external {
        uint mitcoins_bought = usd_invested * usd_to_mitcoins;
        equity_mitcoins[investor] += mitcoins_bought;
        equity_usd[investor] = equity_mitcoins[investor] / usd_to_mitcoins;
        total_mitcoins_bought += mitcoins_bought;
    }
}
