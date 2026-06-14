// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";

contract PharosNFT is ERC721URIStorage, ERC721Enumerable, Ownable, IERC2981 {
    uint256 private _nextTokenId;
    uint256 public mintPrice;
    uint256 public maxSupply;
    string public contractURI;
    address public royaltyReceiver;
    uint96 public royaltyFraction;

    event MetadataUpdate(uint256 indexed tokenId, string uri);
    event CollectionDeployed(string name, string symbol, uint256 maxSupply, uint256 mintPrice);
    event TokenMinted(address indexed to, uint256 indexed tokenId, string uri);

    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _maxSupply,
        uint256 _mintPrice,
        address _royaltyReceiver,
        uint96 _royaltyFraction,
        string memory _contractURI
    ) ERC721(_name, _symbol) Ownable(msg.sender) {
        maxSupply = _maxSupply;
        mintPrice = _mintPrice;
        royaltyReceiver = _royaltyReceiver;
        royaltyFraction = _royaltyFraction;
        contractURI = _contractURI;
        _nextTokenId = 1;
        emit CollectionDeployed(_name, _symbol, _maxSupply, _mintPrice);
    }

    function safeMint(address to, string memory uri) public payable returns (uint256) {
        require(msg.value >= mintPrice, "Insufficient payment");
        require(_nextTokenId <= maxSupply, "Max supply reached");
        uint256 tokenId = _nextTokenId;
        _nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        emit TokenMinted(to, tokenId, uri);
        return tokenId;
    }

    function mintBatch(address[] memory recipients, string[] memory uris) public payable {
        require(recipients.length == uris.length, "Array length mismatch");
        require(recipients.length > 0, "Empty arrays");
        require(msg.value >= mintPrice * recipients.length, "Insufficient payment");
        require(_nextTokenId + recipients.length - 1 <= maxSupply, "Max supply would be exceeded");
        for (uint256 i = 0; i < recipients.length; i++) {
            uint256 tokenId = _nextTokenId;
            _nextTokenId++;
            _safeMint(recipients[i], tokenId);
            _setTokenURI(tokenId, uris[i]);
            emit TokenMinted(recipients[i], tokenId, uris[i]);
        }
    }

    function setTokenURI(uint256 tokenId, string memory uri) public onlyOwner {
        require(ownerOf(tokenId) != address(0), "Token does not exist");
        _setTokenURI(tokenId, uri);
        emit MetadataUpdate(tokenId, uri);
    }

    function setContractURI(string memory _contractURI) public onlyOwner {
        contractURI = _contractURI;
    }

    function setMintPrice(uint256 _mintPrice) public onlyOwner {
        mintPrice = _mintPrice;
    }

    function setRoyaltyReceiver(address _receiver) public onlyOwner {
        royaltyReceiver = _receiver;
    }

    function setRoyaltyFraction(uint96 _fraction) public onlyOwner {
        royaltyFraction = _fraction;
    }

    function withdraw() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance");
        payable(owner()).transfer(balance);
    }

    function totalSupply() public view override returns (uint256) {
        return _nextTokenId - 1;
    }

    function royaltyInfo(uint256, uint256 salePrice) public view override returns (address, uint256) {
        uint256 royaltyAmount = (salePrice * royaltyFraction) / _feeDenominator();
        return (royaltyReceiver, royaltyAmount);
    }

    function _feeDenominator() internal pure virtual returns (uint96) {
        return 10000;
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721URIStorage, ERC721Enumerable, IERC165) returns (bool) {
        return interfaceId == type(IERC2981).interfaceId || super.supportsInterface(interfaceId);
    }

    function _increaseBalance(address account, uint128 value) internal override(ERC721, ERC721Enumerable) {
        super._increaseBalance(account, value);
    }

    function _update(address to, uint256 tokenId, address auth) internal override(ERC721, ERC721Enumerable) returns (address) {
        return super._update(to, tokenId, auth);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
}
