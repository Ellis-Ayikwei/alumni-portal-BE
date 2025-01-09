#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Insurance Packages """

from colorama import Fore
from flask import Flask, json, jsonify, request, abort
from models import storage
from models.benefit import Benefit
from models.insurance_package import InsurancePackage, PaymentFrequency

from api.v1.src.views import app_views

@app_views.route("/insurance_packages", methods=["GET"], strict_slashes=False)
def get_all_insurance_packages():
    """Retrieve all insurance packages"""
    insurance_packages = storage.all(InsurancePackage).values()
    insurance_packages_list = []
    for package in insurance_packages:
        package_dict = package.to_dict()
        benefits_list = []
        for benefit in package.benefits:
            benefits_list.append(benefit.to_dict())
        package_dict["benefits"] = benefits_list
        package_dict["groups"] = [group.to_dict() for group in package.groups]
        insurance_packages_list.append(package_dict)
    return jsonify(insurance_packages_list), 200


INSURANCE_PACKAGE_NOT_FOUND = "Insurance package not found"

@app_views.route("/insurance_packages/<package_id>", methods=["GET"])
def get_insurance_package_by_id(package_id):
    """Retrieve a specific insurance package by ID"""
    package = storage.get(InsurancePackage, package_id)
    if package is None:
        abort(404, description=INSURANCE_PACKAGE_NOT_FOUND)
    ben_lis_dct = [benefit.to_dict() for benefit in package.benefits]
    package_dict = package.to_dict()
    package_dict["benefits"] = ben_lis_dct

    return jsonify(package_dict), 200


@app_views.route("/insurance_packages", methods=["POST"])
def create_insurance_package():
    """Create a new insurance package"""
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")
    # print(json.dumps(data, indent=4))
    required_fields = [
        "name",
        "description",
        "sum_assured",
        "monthly_premium_ghs",
        "annual_premium_ghs",
    ]
    for field in required_fields:
        if field not in data or not data[field]:
            abort(400, description=f"Missing {field}")
    
    
    filtered_data = {key: value for key, value in data.items() if key != "benefits"}
    new_insurance_package = InsurancePackage(**filtered_data)
    new_insurance_package.save()
    print(f"{Fore.GREEN} - the new package{json.dumps(data, indent=4)}" )
    
    # for k,v in data["bnfs"].items():
    #     new_benefit = Benefit(
    #         name=k,
    #         package_id=new_insurance_package.id,
    #         premium_payable=v,
    #     )
    #     new_benefit.save()
        
    for benefit in data["benefits"]:
        new_benefit = Benefit(
            name=benefit["label"],
            package_id=new_insurance_package.id,
            premium_payable=benefit["premium_payable"],
        )
        new_benefit.save()

    return jsonify(new_insurance_package.to_dict()), 201


# @app_views.route("/insurance_packages/<package_id>", methods=["PUT"])
# def update_insurance_package(package_id):
#     """Update an existing insurance package"""
#     package = storage.get(InsurancePackage, package_id)
#     if package is None:
#         abort(404, description=INSURANCE_PACKAGE_NOT_FOUND)

#     if not request.get_json():
#         abort(400, description="Not a JSON")

#     data = request.get_json()
#     print(data)
#     ignored_fields = [
#         "id",
#         "created_at",
#         "updated_at",
#         "__class__",
#         "benefits",
#         "groups",
#         "package_id",
#     ]
    
#     for key, value in data.items():
#         if key not in ignored_fields:
#             setattr(package, key, value)
    
#     if "benefits" in data:
#         for benefit_data in data["benefits"]:
#             benefit = storage.get(Benefit, benefit_data["id"])
#             if benefit is None:
#                 continue
#             for key, value in benefit_data.items():
#                 if key not in ignored_fields:
#                     setattr(benefit, key, value)
#             benefit.save()

#     storage.save()
#     return jsonify(package.to_dict()), 200



@app_views.route("/insurance_packages/<package_id>", methods=["PUT"])
def update_insurance_package(package_id: str) -> tuple:
    """Update an existing insurance package, including adding or deleting benefits."""
    package = storage.get(InsurancePackage, package_id)
    if package is None:
        abort(404, description="Insurance package not found")

    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")


    print(json.dumps(data, indent=4))
    ignored_fields = [
        "id",
        "created_at",
        "updated_at",
        "__class__",
        "benefits",
        "groups",
        "package_id",
    ]

    # Update package attributes
    for key, value in data.items():
        if key not in ignored_fields:
            setattr(package, key, value)

    # Handle benefits update
    if "benefits" in data:
        updated_benefit_ids = {benefit_data.get("id") for benefit_data in data["benefits"] if "id" in benefit_data}
        existing_benefit_ids = {benefit.id for benefit in package.benefits}
        print("updates: ", updated_benefit_ids)
        print("existing: ", existing_benefit_ids)
                
        
        # Delete removed benefits
        for benefit_id in existing_benefit_ids - updated_benefit_ids:
            benefit = storage.get(Benefit, benefit_id)
            if benefit:
                storage.delete(benefit)

        # Update existing benefits or add new ones
        for benefit_data in data["benefits"]:
            if "id" in benefit_data and benefit_data["id"] in existing_benefit_ids:
                # Update existing benefit
                benefit = storage.get(Benefit, benefit_data["id"])
                if benefit:
                    for key, value in benefit_data.items():
                        print(key, value)
                        if key not in ignored_fields:
                            setattr(benefit, key, value)
                    benefit.save()
            else:
                # Add new benefit
                new_benefit = Benefit(
                    name=benefit_data.get("label"),
                    package_id=package_id,
                    premium_payable=benefit_data.get("premium_payable"),
                )
                new_benefit.save()

    # Save package changes
    storage.save()
    return jsonify({"message": "Insurance package updated successfully"}), 200




@app_views.route("/insurance_packages/<package_id>", methods=["DELETE"])
def delete_insurance_package(package_id):
    """Delete an insurance package"""
    package = storage.get(InsurancePackage, package_id)
    if package is None:
        abort(404, description=INSURANCE_PACKAGE_NOT_FOUND)
    if package is None:
        abort(404, description="Insurance package not found")

    storage.delete(package)
    storage.save()
    return jsonify({}), 200
