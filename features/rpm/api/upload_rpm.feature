@only.with_not_present=2620
Feature: Uploading RPM

  Background:
    Given an rpm
    And an rpm repository

  Scenario: Upload RPM to repository and publish it.
    When an rpm is uploaded
    And the repository is published
    Then the rpm is in the published metadata
