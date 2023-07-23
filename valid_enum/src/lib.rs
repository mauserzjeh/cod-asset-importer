use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, Data, DeriveInput, Error, Ident, Result};

fn check_primitive_type(attr_type: &Ident) -> Result<()> {
    let allowed_types = &[
        "i8", "i16", "i32", "i64", "i128", "isize", "u8", "u16", "u32", "u64", "u128", "usize",
        "f32", "f64", "char",
    ];
    let attr_type_str = attr_type.to_string();
    if allowed_types.contains(&attr_type_str.as_str()) {
        Ok(())
    } else {
        Err(Error::new_spanned(
            attr_type,
            format!(
                "Invalid type. `ValidEnum` macro only supports the following primitive types: {}",
                allowed_types.join(" ")
            ),
        ))
    }
}

#[proc_macro_derive(ValidEnum, attributes(valid_enum))]
pub fn valid_enum_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let enum_name = &input.ident;

    // Extract the `valid_enum` attribute if it exists
    let valid_enum_attr = input
        .attrs
        .iter()
        .find(|attr| attr.path().is_ident("valid_enum"));

    let attr_type = match valid_enum_attr {
        Some(valid_enum_attr) => {
            // Parse the args of the macro
            let args: Ident = valid_enum_attr.parse_args().unwrap();

            args
        }
        None => panic!("ValidEnum missing `valid_enum` attribute"),
    };

    // Check if the provided type is valid
    match check_primitive_type(&attr_type) {
        Ok(_) => (),
        Err(error) => panic!("{}", error)
    }

    if let Data::Enum(data_enum) = &input.data {
        if data_enum.variants.is_empty() {
            panic!("ValidEnum can only be used with enums with variants");
        }

        // Process only enums with unit variants (no data associated with variants)
        if data_enum
            .variants
            .iter()
            .all(|variant| variant.fields.is_empty())
        {
            let match_arms = data_enum.variants.iter().map(|variant| {
                let variant_name = &variant.ident;
                quote! {
                    version if version == #enum_name::#variant_name as #attr_type => Some(#enum_name::#variant_name),
                }
            });

            let generated = quote! {
                impl #enum_name {
                    pub fn valid(version: #attr_type) -> Option<#enum_name> {
                        match version {
                            #(#match_arms)*
                            _ => None
                        }
                    }
                }
            };

            return generated.into();
        } else {
            panic!("ValidEnum can only be used with enums with unit variants");
        }
    }

    panic!("ValidEnum can only be used with enums");
}
