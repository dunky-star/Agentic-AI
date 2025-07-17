import pytest
import json
import time
from pydantic import ValidationError

from code.pydantic_playground.product_model import Product, ProductListingAI

# Test 1: Schema Validation and Structure
class TestProductListingAI:

    @pytest.fixture
    def product_ai(self):
        """Create a product listing AI instance for testing."""
        return ProductListingAI()

    def test_schema_validation(self, product_ai):
        """Test that output conforms to Product schema."""
        description = "Two kilos of fresh tomatoes"

        result = product_ai.generate_product_listing(description)

        # Assert result is a Product instance
        assert isinstance(result, Product)

        # Assert all required fields are present and correct types
        assert isinstance(result.name, str)
        assert isinstance(result.price, float)
        assert isinstance(result.features, list)
        assert isinstance(result.category, str)

        # Assert features list contains strings
        assert all(isinstance(feature, str) for feature in result.features)

        # Assert fields are not empty
        assert len(result.name) > 0
        assert result.price > 0
        assert len(result.features) > 0
        assert len(result.category) > 0


    # Test 2: Content Relevance and Accuracy
    def test_content_relevance(self, product_ai):
        """Test that generated content is relevant to input description."""
        test_cases = [
            {
                "description": "Fresh organic apples from local farm",
                "expected_keywords": ["apple", "organic", "fresh"],
                "expected_category": "Grocery"
            },
            {
                "description": "Cold brew coffee concentrate",
                "expected_keywords": ["coffee", "brew", "concentrate"],
                "expected_category": "Beverages"
            },
            {
                "description": "Greek yogurt with honey",
                "expected_keywords": ["yogurt", "greek", "honey"],
                "expected_category": "Dairy"
            }
        ]

        for case in test_cases:
            result = product_ai.generate_product_listing(case["description"])

            # Test name relevance
            name_lower = result.name.lower()
            assert any(keyword in name_lower for keyword in case["expected_keywords"])

            # Test category accuracy
            assert result.category == case["expected_category"]

            # Test features relevance
            features_text = " ".join(result.features).lower()
            assert any(keyword in features_text for keyword in case["expected_keywords"])


    # Test 3: Price Reasonableness
    def test_price_reasonableness(self, product_ai):
        """Test that generated prices are reasonable."""
        test_cases = [
            ("Single banana", 0.1, 2.0),  # Should be cheap
            ("Premium olive oil 500ml", 8.0, 50.0),  # Should be moderate
            ("Organic grass-fed beef 1kg", 15.0, 100.0),  # Should be expensive
        ]

        for description, min_price, max_price in test_cases:
            result = product_ai.generate_product_listing(description)

            # Assert price is within reasonable range
            assert min_price <= result.price <= max_price, f"Price {result.price} not in range [{min_price}, {max_price}] for {description}"

            # Assert price has reasonable precision (max 2 decimal places)
            assert round(result.price, 2) == result.price


    # Test 4: Feature Quality and Quantity
    def test_feature_quality(self, product_ai):
        """Test that generated features are meaningful and appropriate."""
        description = "Artisanal sourdough bread"

        result = product_ai.generate_product_listing(description)

        # Assert reasonable number of features
        assert 2 <= len(result.features) <= 8, f"Expected 2-8 features, got {len(result.features)}"

        # Assert features are substantial (not just single words)
        for feature in result.features:
            assert len(feature.split()) >= 2, f"Feature '{feature}' too short"
            assert len(feature) <= 100, f"Feature '{feature}' too long"

        # Assert features are unique (no duplicates)
        assert len(result.features) == len(set(result.features))

        # Assert features are relevant to bread
        bread_keywords = ["bread", "sourdough", "artisanal", "bake", "crust", "texture", "flavor"]
        features_text = " ".join(result.features).lower()
        keyword_matches = sum(1 for keyword in bread_keywords if keyword in features_text)
        assert keyword_matches >= 1, "Features should mention bread-related terms"


    # Test 5: Category Constraint Validation
    def test_category_constraints(self, product_ai):
        """Test that AI respects predefined category constraints."""
        valid_categories = ["Beverages", "Dairy", "Grocery"]

        test_descriptions = [
            "Fresh orange juice",
            "Whole milk",
            "Canned tomatoes",
            "Sparkling water",
            "Cheese slices",
            "Pasta noodles"
        ]

        for description in test_descriptions:
            result = product_ai.generate_product_listing(description)

            # Assert category is one of the valid options
            assert result.category in valid_categories, f"Invalid category '{result.category}' for '{description}'"

    # Test 6: Edge Cases and Error Handling
    def test_edge_cases(self, product_ai):
        """Test AI behavior with edge cases."""
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "x",  # Single character
            "a" * 500,  # Very long string
            "??????? unknown product ???????",  # Unclear description
            "123456789",  # Numbers only
        ]

        for description in edge_cases:
            try:
                result = product_ai.generate_product_listing(description)

                # If it doesn't raise an exception, validate the output
                assert isinstance(result, Product)
                assert len(result.name) > 0
                assert result.price > 0
                assert len(result.features) > 0
                assert result.category in ["Beverages", "Dairy", "Grocery"]

            except Exception as e:
                # If an exception is raised, it should be a specific, handled type
                assert isinstance(e, (ValueError, ValidationError))

    # Test 7: Consistency Testing
    def test_consistency(self, product_ai):
        """Test that similar inputs produce consistent results."""
        similar_descriptions = [
            "Fresh red tomatoes",
            "Ripe red tomatoes",
            "Fresh tomatoes, red variety"
        ]

        results = [product_ai.generate_product_listing(desc) for desc in similar_descriptions]

        # All should be in the same category
        categories = [result.category for result in results]
        assert len(set(categories)) == 1, f"Expected same category, got {categories}"

        # Prices should be reasonably similar (within 50% of each other)
        prices = [result.price for result in results]
        price_range = max(prices) - min(prices)
        avg_price = sum(prices) / len(prices)
        assert price_range / avg_price <= 0.5, f"Price variation too high: {prices}"

        # Names should all contain "tomato"
        names = [result.name.lower() for result in results]
        assert all("tomato" in name for name in names)

    # Test 8: Performance Testing

    def test_response_time(self, product_ai):
        """Test that AI responds within acceptable time limits."""
        description = "Organic free-range chicken breast"

        start_time = time.time()
        result = product_ai.generate_product_listing(description)
        end_time = time.time()

        response_time = end_time - start_time

        # Assert reasonable response time (adjust based on your requirements)
        assert response_time < 10.0, f"Response took {response_time:.2f} seconds, expected < 10s"

        # Assert we got a valid result
        assert isinstance(result,Product)